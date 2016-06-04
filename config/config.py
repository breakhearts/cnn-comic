import os

USE_GPU = False

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

data_dir = os.path.join(base_path, "data")
model_dir = os.path.join(data_dir, "model")

if not os.path.exists(data_dir):
    os.mkdir(data_dir)
if not os.path.exists(model_dir):
    os.mkdir(model_dir)

network = "inception-bn"
data_dir = os.path.join(base_path, "data")
save_model_prefix = os.path.join(model_dir, "comic")
num_epochs = 20
num_classes = 300
num_examples = 10000
batch_size = 32
lr = 0.1
lr_factor = 0.94
lr_factor_epoch = 1
log_file = "comic.log"
log_dir = os.path.join(base_path, "logs")
train_dataset = "comic_train.rec"
val_dataset = "comic_val.rec"
data_shape = 224

pretrained_model = os.path.join(base_path, "Inception/Inception_BN")
pretrained_epoch = 39
kv_store="local"

if USE_GPU:
    gpus = "0"
else:
    gpus = None