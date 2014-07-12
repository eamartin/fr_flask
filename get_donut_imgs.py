#! python
import urllib2
import sys
from BeautifulSoup import BeautifulSoup
import re
import os

nums_to_pics_map = open("num_to_pics.txt", 'w')
nums_to_pics_map.write("# name, pic_num\n")

def main():
    if (len(sys.argv) != 2):
        print "Usage " + sys.argv[0] + " url_to_grab"
        exit(1)
    url = sys.argv[1]
    pg = urllib2.urlopen(url)
    page = BeautifulSoup(urllib2.urlopen(url))
    imgs = page.findAll(imgs_with_show)

    for idx, img_tag in enumerate(imgs[:2]):
        img_url = "http://donut.caltech.edu/directory/" + img_tag['src']
        img = urllib2.urlopen(img_url)
        fd = open("prefrosh_images/%d.jpg" % idx, 'w')
        fd.write(img.read())
        nums_to_pics_map.write(img_tag.parent.contents[3] +  ", " + "%03d\n" % idx)


def imgs_with_show(tag):
    return tag.name == 'img' and tag['src'] and not re.match('.*noshow.*', tag['src'])

if __name__ == "__main__":
    try:
        os.mkdir("prefrosh_images")
    except OSError:
        pass
    main()
