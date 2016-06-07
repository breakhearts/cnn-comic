from PIL import Image
import numpy as np
import mxnet as mx


def get_image_array(path, show_img=False):
    # load image
    #img = io.imread(path)
    img = Image.open(path)
    img = img.convert('RGB')
    # we crop image from center
    short_edge = min(img.size)
    yy = int((img.size[0] - short_edge) / 2)
    xx = int((img.size[1] - short_edge) / 2)
    box=(yy, xx, yy + short_edge, xx + short_edge)
    crop_img = img.crop(box)
    # resize to 224, 224
    #resized_img = img.resize(crop_img, (224, 224))
    resized_img = crop_img.resize(size=(224,224))
    # convert to numpy.ndarray
    # sample = np.asarray(resized_img) * 256
    sample = np.asarray(resized_img)

    # swap axes to make image from (224, 224, 4) to (3, 224, 224)

    sample = np.swapaxes(sample, 0, 2)
    sample = np.swapaxes(sample, 1, 2)
    # sub mean
    #normed_img = sample - mean_img.asnumpy()
    r = 123.68
    g = 116.779
    b = 103.939
    x = y = 224
    r_channel = np.ones([1, x, y])*r
    g_channel = np.ones([1, x, y])*g
    b_channel = np.ones([1, x, y])*b
    normed_img = sample - np.concatenate((r_channel, g_channel, b_channel), axis=0)
    normed_img.resize(1, 3, 224, 224)
    return normed_img


def load_model(prefix, num_round, ctx = mx.gpu()):
    model = mx.model.FeedForward.load(prefix, num_round, ctx=ctx, numpy_batch_size=24)
    return model


def predict_file(model, filename):
    batch = get_image_array(filename)
    prob = model.predict(batch)[0]
    pred = np.argsort(prob)[::-1]
    t = zip(pred, prob)
    t.sort(cmp=lambda x, y: int(y[1] * 1000 - x[1] * 1000))
    return t