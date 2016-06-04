# -*-coding=utf-8 -*-
import requests
import hashlib
import os
import json
import urllib
from multiprocessing import Process, Queue


def request_with_ua(url):
    headers = {
        "Content-type": "image/jpeg",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
    }
    r = requests.get(url, headers=headers, timeout=10)
    return r


def decode_img_url(s):
    dic = {
        "0": "7",   "1": "d",   "2": "g",   "3": "j",   "4": "m",   "5": "o",   "6": "r",   "7": "u",   "8": "1",
        "9": "4",   "a": "0",   "b": "8",   "c": "5",   "d": "2",   "e": "v",   "f": "s",   "g": "n",   "h": "k",
        "i": "h",   "j": "e",   "k": "b",   "l": "9",   "m": "6",   "n": "3",   "o": "w",   "p": "t",   "q": "q",
        "r": "p",   "s": "l",   "t": "i",   "u": "f",   "v": "c",   "w": "a"
    }
    s = s.replace("AzdH3F","/")
    s = s.replace("_z2C$q", ":")
    s = s.replace("_z&e3B", ".")
    p = ""
    for i in s:
        if i in dic.keys():
            p += dic[i]
        else:
            p += i
    return p


def download_img(root, url, count):
    ext = url.split(".")[-1].split("?")[0]
    filename = "%03d_" % count + hashlib.sha224(url).hexdigest() + "." + ext
    path = os.path.join(root, filename)
    r = request_with_ua(url)
    if r.status_code == 200:
        with open(path, "wb") as f:
            f.write(r.content)
    else:
        print "download {0} failed".format(url)


def query_img(root, q):
    while not q.empty():
        query = q.get()
        rn = 50
        pn = 0
        downloaded = {

        }
        count = 0
        while count < 1000:
            url = 'http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord=ss&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=&z=&ic=&word={0}&s=&se=&tab=&width=&height=&face=&istype=&qc=&nc=1&fr=&pn={1}&rn={2}&gsm=1fe&1463479205503='.format(urllib.quote(query), pn, rn)
            try:
                r = request_with_ua(url)
            except:
                import time
                time.sleep(30)
                continue
            if r.status_code == 200:
                c = r.content
                try:
                    obj = json.loads(c)
                except:
                    print c
                if len(obj["data"]) < 2:
                    break
                for t in obj["data"]:
                    if "objURL" in t:
                        url = decode_img_url(t["objURL"])
                        print query.decode("utf-8"), url
                        dir = os.path.join(root, query.decode("utf-8"))
                        if not os.path.exists(dir):
                            os.mkdir(dir)
                        if url not in downloaded:
                            try:
                                download_img(dir, url, count)
                                count += 1
                            except:
                                print "download {0} failed".format(url)
                            downloaded[url] = True
                        else:
                            print "{0} already downloaded".format(url)
            pn += rn


def get_list(root, filename, concurrent=10):
    q = Queue()
    with open(filename, "rb") as f:
        for lineno, line in enumerate(f):
            name = line.strip()
            if name == "":
                continue
            q.put(name)
    proecess = [

    ]
    for i in range(concurrent):
        p = Process(target=query_img, args=(root, q))
        p.start()
        proecess.append(p)
    for p in proecess:
        p.join()

if __name__ == "__main__":
    get_list("../data", "comic_list", 10)
