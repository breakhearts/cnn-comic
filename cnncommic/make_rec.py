# -*- coding:utf-8 -*-
import os
import random
from PIL import Image
import mxnet as mx
import numpy as np
import time


def list_image(root, exts):
    image_list = []
    cat = {}
    for path, subdirs, files in os.walk(root):
        print len(cat), path
        for fname in files:
            fpath = os.path.join(path, fname)
            suffix = os.path.splitext(fname)[1].lower()
            if os.path.isfile(fpath) and (suffix in exts):
                if path not in cat:
                    cat[path] = len(cat)
                image_list.append((len(image_list), os.path.relpath(fpath, root), cat[path]))
    return image_list, cat


def write_list(path_out, image_list):
    with open(path_out, 'w') as fout:
        for i in xrange(len(image_list)):
            line = '%d\t'%image_list[i][0]
            for j in image_list[i][2:]:
                line += '%f\t'%j
            line += '%s\n'%image_list[i][1]
            fout.write(line)


def write_cat_map(path_out, cat):
    with open(path_out, 'w') as fout:
        for path, cat_index in cat.items():
            fout.write("{0}\t{1}\n".format(cat_index, path))


def make_list(prefix_out, root, exts, num_chunks, train_ratio):
    image_list, cat_map = list_image(root, exts)
    random.shuffle(image_list)
    N = len(image_list)
    chunk_size = (N+num_chunks-1)/num_chunks
    for i in xrange(num_chunks):
        chunk = image_list[i*chunk_size:(i+1)*chunk_size]
        if num_chunks > 1:
            str_chunk = '_%d'%i
        else:
            str_chunk = ''
        if train_ratio < 1:
            sep = int(chunk_size*train_ratio)
            write_list(prefix_out+str_chunk+'_train.lst', chunk[:sep])
            write_list(prefix_out+str_chunk+'_val.lst', chunk[sep:])
        else:
            write_list(prefix_out+str_chunk+'.lst', chunk)
        write_cat_map(prefix_out+ "_cat_map.txt", cat_map)


def read_list(path_in):
    image_list = []
    with open(path_in) as fin:
        for line in fin.readlines():
            line = [i.strip() for i in line.strip().split('\t')]
            item = [int(line[0])] + [line[-1]] + [float(i) for i in line[1:-1]]
            image_list.append(item)
    return image_list


def write_record(root, image_list, rec_file_name):

    def image_encode(item):
        try:
            img = Image.open(os.path.join(root, item[1]))
            img = img.convert('RGB')
        except Exception as e:
            print 'read none error:', item[1]
            return
        short_egde = min(img.size)
        yy = int((img.size[0] - short_egde) / 2)
        xx = int((img.size[1] - short_egde) / 2)
        box=(xx, yy, xx + short_egde, yy + short_egde)
        crop_img = img.crop(box)
        resized_img = crop_img.resize(size=(224,224))
        header = mx.recordio.IRHeader(0, item[2], item[0], 0)
        sample = np.asarray(resized_img)
        try:
            s = mx.recordio.pack_img(header, sample, quality=100, img_fmt=".jpg")
            return s
        except Exception as e:
            print 'pack_img error:', item[1]

    record = mx.recordio.MXRecordIO(rec_file_name, 'w')
    cnt = 0
    pre_time = time.time()
    for item in image_list:
        s = image_encode(item)
        if not s:
            continue
        record.write(s)
        cnt += 1
        if cnt % 1000 == 0:
            cur_time = time.time()
            print 'time:', cur_time - pre_time, 'count:', cnt
            pre_time = cur_time

