# -*-coding:utf-8-*-

"""
get top 300 comic from bangumi.tv
"""
from lxml import etree
import requests


def get_comic_list(count):
    comic_list = []
    for i in xrange(200):
        url = "http://bangumi.tv/anime/browser/?sort=rank&page={0}".format(i + 1)
        r = requests.get(url)
        if r.status_code != 200:
            print "download page error, quit"
            break
        root = etree.HTML(r.content)
        for item in root.xpath('//ul[@id="browserItemList"]/li/div[@class="inner"]/h3/a/text()'):
            name = item.encode("utf-8")
            print name
            comic_list.append(name)
            if len(comic_list) >= count:
                return comic_list
    return comic_list


def remove_duplication(comic_list):
    comic_list = [x.split("OVA")[0].strip() for x in comic_list]
    comic_list = [x.split("剧场版")[0].strip() for x in comic_list]
    comic_list.sort(key=lambda x: (x, len(x)))
    new_comic_list = []
    i = 0
    while i < len(comic_list):
        name = comic_list[i]
        new_comic_list.append(name)
        if i == len(comic_list) - 1:
            return new_comic_list
        for j in xrange(i+1, len(comic_list)):
            if comic_list[j].startswith(name):
                print "remove {0} because duplicate of {1}".format(comic_list[j], name)
                i = j + 1
            else:
                i = j
                break
    return new_comic_list


def save_comic_list(comic_list, filename):
    with open(filename, "wb") as f:
        for comic in comic_list:
            f.write("{0}\n".format(comic))

if __name__ == "__main__":
    comic_list = get_comic_list(300)
    comic_list = remove_duplication(comic_list)
    save_comic_list(comic_list, "comic_list_unsort.txt")