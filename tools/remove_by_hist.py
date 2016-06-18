# -*- coding:utf-8 -*-
from PIL import Image
import numpy as np
import os
import shutil


def wise_mk_dir(path):
    if path == "":
        return
    if os.path.exists(path):
        return
    p, c = os.path.split(path)
    if not os.path.exists(p):
        wise_mk_dir(p)
    os.mkdir(path)


def wise_mk_dir_for_file(filepath):
    p = os.path.dirname(filepath)
    wise_mk_dir(p)


def is_remove(fname):
    try:
        img = Image.open(fname)
        img = img.convert("HSV")
    except:
        return True
    h,s,v = img.split()
    s = np.ravel(np.array(s))
    hist, _ = np.histogram(s, bins=255)
    hist = hist > 50
    return np.count_nonzero(hist) < 50


def split_photo(img_root, photo_root):
    for p, _ , files in os.walk(img_root):
        for fname in files:
            ext = fname.split(".")[-1].lower()
            if ext not in ["jpg","png"]:
                continue
            fp = os.path.join(p, fname)
            print fp
            if is_remove(fp):
                dst = os.path.dirname(os.path.join(photo_root, os.path.relpath(fp, img_root)))
                wise_mk_dir(dst)
                print "Move {0} to {1}".format(fp, dst)
                shutil.move(fp, dst)

split_photo("d:\data", "d:\data_photo")