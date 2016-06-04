from __future__ import absolute_import
from cnncommic import make_rec
from config import config
from cnncommic import train
import os


make_rec.make_list(os.path.join(config.data_dir, "comic"), config.data_dir, [".jpg", ".png"], 1, 0.8)
image_list = make_rec.read_list(os.path.join(config.data_dir, "comic_train.lst"))
make_rec.write_record(config.data_dir, image_list, os.path.join(config.data_dir, config.train_dataset))
image_list = make_rec.read_list(os.path.join(config.data_dir, "comic_val.lst"))
make_rec.write_record(config.data_dir, image_list, os.path.join(config.data_dir, config.val_dataset))

train.fit(config, train.get_symbol(), train.get_iterator)
