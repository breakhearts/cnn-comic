network = "inception-bn"
data_dir = "../data/comic"
save_model_prefix = "../data/model/comic"
num_epoch = 20
num_classes = 300
num_examples = 10000
batch_size = 128
lr = 0.1
lr_factor = 0.94
log_file = "comic.log"
log_dir = "../logs"
train_dataset = "comic_train.rec"
val_dataset = "comic_val.rec"
data_shape = 224

pretrained_model = "Inception/Inception_BN"
pretrained_epoch = "39"
