from cnncommic import predict
import os
import mxnet as mx
import shutil

CARTOON = 0
PHOTO = 1

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


def split_photo(model_prefix, model_round, img_root, photo_root, ctx = mx.gpu()):
    model = predict.load_model(model_prefix, model_round, ctx= ctx)
    for p, _ , files in os.walk(img_root):
        for fname in files:
            ext = fname.split(".")[-1].lower()
            if ext not in ["jpg","png"]:
                continue
            fp = os.path.join(p, fname)
            print fp
            try:
                t =  predict.predict_file(model, fp)
                print t
                if t[0][0] == PHOTO:
                    dst = os.path.dirname(os.path.join(photo_root, os.path.relpath(fp, img_root)))
                    wise_mk_dir(dst)
                    print "Move {0} to {1}".format(fp, dst)
                    shutil.move(fp, dst)
            except:
                print "error"

if __name__ == "__main__":
    split_photo("../model/cartoon", 30, "d:/data", "d:/data_photo")