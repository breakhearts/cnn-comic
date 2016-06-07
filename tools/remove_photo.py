from cnncommic import predict
import os
import mxnet as mx

CARTOON = 0
PHOTO = 1

def split_photo(model_prefix, model_round, img_root, photo_root):
    model = predict.load_model(model_prefix, model_round, ctx= mx.cpu())
    for p, _ , files in os.walk(img_root):
        for fname in files:
            ext = fname.split(".")[-1].lower()
            if ext not in ["jpg","png"]:
                continue
            fp = os.path.join(p, fname)
            print fp
            try:
                print predict.predict_file(model, fp)
            except:
                print "error"

if __name__ == "__main__":
    split_photo("../models/cartoon", 30, "d:/photo", "")