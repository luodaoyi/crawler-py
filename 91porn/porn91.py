#-*- coding=utf-8 -*-
import requests
import re
import os
import sys
import argparse
import datetime
import logging
import time
import random
import string
import threading
import logging
from downloader import Downloader

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
           'X-Forwarded-For': '', 'Accept-Language': 'zh-CN,zh;q=0.8'}
info_reg = re.compile(
    '''<div class="imagechannel[\W\w]*?<a target=blank href="(http://.*?/view_video.*?\.php\?viewkey=.*?)">[\W\w]*?<img src="(.*?)" width="120" title="(.*?)" />''')
mp4_reg = re.compile("""<source src="(.*?)" type='video/mp4'>""")
chars = string.ascii_letters

basedir=os.path.abspath('.')
video_path=os.path.join(basedir,'video')
if not os.path.exists(video_path):
    os.mkdir(video_path)

#找国内可用网址到这里：https://www.ebay.com/usr/91dizhi_1
porn91_url =  'http://91porn.com'#'http://93.91p09.space/'
info_list=[]

def timenow():
    return datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')


def randip():
    return str(random.randint(0, 255)) + "."\
            + str(random.randint(0, 255)) + "."\
            + str(random.randint(0, 255)) + "."\
            + str(random.randint(0, 255))

def randchar(): return ''.join(random.sample(chars, 5))

def exists(id):
    if not os.path.exists('history.txt'):
        return False
    with open('history.txt','r') as f:
        history=[i.strip() for i in f.readlines()]
    if id in history:
        return True
    else:
        return False

def get_list(url):
    logging.info('start parse ' + url)
    videos=[]
    try:
        headers['X-Forwarded-For'] = randip()
        resp = requests.get(url, headers=headers)
        resp.encoding='utf-8'
        cont = resp.text
        urls = info_reg.findall(cont)
        logging.info(url+ ' get {} videos'.format(len(urls)))
        for ul in urls:
            url, picture, title = ul
            url = url.replace('_hd', '')
            id = re.findall('viewkey=(.*?)&', url)[0]
            downpath = os.path.join(video_path,u'{}.mp4'.format(re.sub('[\\/:\*\?"><\|]','',title)))
            if not exists(id):
                videos.append({'id':id, 'url':url, 'picture':picture, 'downpath':downpath,'title':title})
                logging.warning(id + ' do not exists!')
        return videos
    except Exception as e:
        logging.error(e)
        return False


def download_video(**kwargs):
    ds=[]
    url=kwargs['url']
    logging.info('geting video from url {}'.format(url))
    try:
        headers['X-Forwarded-For'] = randip()
        resp = requests.get(url, headers=headers)
        resp.encoding='utf-8'
        cont = resp.text
        videos = mp4_reg.findall(cont)
        if len(videos) <= 0:
            logging.warning('not found video!! next...')
            return None
        video = videos[0]
        d = Downloader(url=video,path=kwargs['downpath'],picture=kwargs['picture'],title=kwargs['title'],id=kwargs['id'])
        return d
    except Exception as e:
        logging.error(e)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', default='new')
    parser.add_argument('-a1', default=1, type=int)
    parser.add_argument('-a2', default=1000, type=int)
    args = parser.parse_args()

    page_base_url = porn91_url + '/video.php?viewtype=basic&category=hd&page=%d'
    pagelists = [page_base_url % x for x in range(args.a1, args.a2 + 1)]
            

    #一页一页下载
    for page in pagelists:
        videopages=get_list(page)
        if videopages != False:
            tasks=[]
            for video in videopages:
                d = download_video(**video)
                if isinstance(d,Downloader):
                    d.run()

        else:
            logging.error('get list fail!')


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    main()
