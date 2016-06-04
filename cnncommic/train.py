from __future__ import absolute_import
import mxnet as mx
import logging
import os
from config import config


import importlib


def get_symbol():
    net = importlib.import_module('cnncommic.symbol_' + config.network).get_symbol(config.num_classes)
    if "pretrained_model" in config.__dict__ and config.pretrained_model and "pretrained_epoch" in config.__dict__ and config.pretrained_epoch:
        model, arg_params, aux_params = mx.model.load_checkpoint(config.pretrained_model, config.pretrained_epoch)
        internals = model.get_internals()
        fea_symbol = internals["flatten_output"]
        fc_l = mx.symbol.FullyConnected(data=fea_symbol, name='fc_l', num_hidden=config.num_classes)
        softmax = mx.symbol.SoftmaxOutput(data=fc_l, name='softmax')
        net = softmax
    return net


# data
def get_iterator(args, kv):
    data_shape = (3, args.data_shape, args.data_shape)
    train = mx.io.ImageRecordIter(
        path_imgrec = os.path.join(args.data_dir, args.train_dataset),
        mean_r      = 123.68,
        mean_g      = 116.779,
        mean_b      = 103.939,
        data_shape  = data_shape,
        batch_size  = args.batch_size,
        rand_crop   = True,
        rand_mirror = True,
        num_parts   = kv.num_workers,
        part_index  = kv.rank)

    val = mx.io.ImageRecordIter(
        path_imgrec = os.path.join(args.data_dir, args.val_dataset),
        mean_r      = 123.68,
        mean_g      = 116.779,
        mean_b      = 103.939,
        rand_crop   = False,
        rand_mirror = False,
        data_shape  = data_shape,
        batch_size  = args.batch_size,
        num_parts   = kv.num_workers,
        part_index  = kv.rank)
    return (train, val)


def fit(args, network, data_loader, batch_end_callback=None):
    # kvstore
    kv = mx.kvstore.create(args.kv_store)

    # logging
    head = '%(asctime)-15s Node[' + str(kv.rank) + '] %(message)s'
    if 'log_file' in args.__dict__ and args.log_file is not None:
        log_file = args.log_file
        log_dir = args.log_dir
        log_file_full_name = os.path.join(log_dir, log_file)
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        logger = logging.getLogger()
        handler = logging.FileHandler(log_file_full_name)
        formatter = logging.Formatter(head)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.info('start with arguments %s', args)
    else:
        logging.basicConfig(level=logging.DEBUG, format=head)
        logging.info('start with arguments %s', args)

    # load model
    #model_prefix = args.model_prefix
    #if model_prefix is not None:
    #    model_prefix += "-%d" % (kv.rank)
    model_args = {}
    #if args.load_epoch is not None:
    #    assert model_prefix is not None
    #    tmp = mx.model.FeedForward.load(model_prefix, args.load_epoch)
    #    model_args = {'arg_params' : tmp.arg_params,
    #                  'aux_params' : tmp.aux_params,
    #                  'begin_epoch' : args.load_epoch}
    # save model
    save_model_prefix = args.save_model_prefix
    #if save_model_prefix is None:
    #    save_model_prefix = model_prefix
    checkpoint = None if save_model_prefix is None else mx.callback.do_checkpoint(save_model_prefix)

    # data
    (train, val) = data_loader(args, kv)

    # train
    devs = mx.cpu() if args.gpus is None else [
        mx.gpu(int(i)) for i in args.gpus.split(',')]

    epoch_size = args.num_examples / args.batch_size

    if args.kv_store == 'dist_sync':
        epoch_size /= kv.num_workers
        model_args['epoch_size'] = epoch_size

    if 'lr_factor' in args.__dict__ and args.lr_factor < 1:
        model_args['lr_scheduler'] = mx.lr_scheduler.FactorScheduler(
            step = max(int(epoch_size * args.lr_factor_epoch), 1),
            factor = args.lr_factor)

    if 'clip_gradient' in args.__dict__ and args.clip_gradient is not None:
        model_args['clip_gradient'] = args.clip_gradient

    # disable kvstore for single device
    if 'local' in kv.type and (
            args.gpus is None or len(args.gpus.split(',')) is 1):
        kv = None

    model = mx.model.FeedForward(
        ctx                = devs,
        symbol             = network,
        num_epoch          = args.num_epochs,
        learning_rate      = args.lr,
        momentum           = 0.9,
        wd                 = 0.00001,
        initializer        = mx.init.Xavier(factor_type="in", magnitude=2.34),
        **model_args)

    eval_metrics = ['accuracy']
    ## TopKAccuracy only allows top_k > 1
    for top_k in [5, 10, 20]:
        eval_metrics.append(mx.metric.create('top_k_accuracy', top_k = top_k))

    if batch_end_callback is not None:
        if not isinstance(batch_end_callback, list):
            batch_end_callback = [batch_end_callback]
    else:
        batch_end_callback = []
    batch_end_callback.append(mx.callback.Speedometer(args.batch_size, 50))

    model.fit(
        X                  = train,
        eval_data          = val,
        eval_metric        = eval_metrics,
        kvstore            = kv,
        batch_end_callback = batch_end_callback,
        epoch_end_callback = checkpoint)


# train
if __name__ == "__main__":
    fit(config, get_symbol(), get_iterator)