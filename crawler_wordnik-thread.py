#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function, absolute_import

import gevent.monkey
import gevent.pool
gevent.monkey.patch_all()

from collections import OrderedDict
from datetime import datetime
from importlib import import_module
from requests.models import Response
import click
import copy
import glob
import html2text
import itertools
import json
import logging
import math
import os
import random
import re
import requests
import signal
import sys
import time
#import urllib.request

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class WiktionaryCrawler:

    def __init__(self, input_proxies_file, json_output_path, process_seq=0, process_count=1):
        self.pool = gevent.pool.Pool(400)
        self.word_list = []
        self.proxy_anchor = 0
        self.proxy_list = []
        self.downloaded = 0
        self.word_retry = {}
        self.proxies_hash = {}
        self.json_output_path = json_output_path
        
        # 多进程模式
        self.process_seq   = process_seq
        self.process_count = process_count

        self.load_proxies(input_proxies_file)
        random.shuffle(self.proxy_list) # 打乱列表, 避免不同scheme, 相同IP/Port的相连.
        
        self.load_word_list()

    def get_wiki_json(self, word):
        proxy = self.next_proxy()
        try:
            self.process_proxies_info(proxy, { 'request': '1' })
            # 代理的请求+1
            proxy['request'] += 1
            # 请求URL, 获得json返回
            host = proxy.get('host')
            port = proxy.get('port')
            scheme = proxy['type']

            request_proxies = { scheme: "%s:%s" % (host, port) }
            if scheme == 'socks4' or scheme == 'socks5':
                request_proxies = { 'http': "http://%s:%s" % (host, port), 'https': "https://%s:%s" % (host, port) }
                scheme = 'https'
            # https://www.wordnik.com/words/hello
            url = "%s://www.wordnik.com/words/"  % (scheme)
            r = requests.get( url + word,proxies=request_proxies, timeout=20, verify=False)
            # 成功
            if r.status_code is 200:
                self.process_proxies_info(proxy, { 'success': '1' })
                return (word, r.content, None)
            else:
                return (word, None, r.status_code)
            #return (word, None, 500)
        except requests.exceptions.ProxyError:
            self.process_proxies_info(proxy, { 'failure': '1' })
            return (word, None, "ProxyError")
        except Exception:
            self.process_proxies_info(proxy, { 'refused': '1' })
            return (word, None, "Error")

    def batch_download_words(self, words):
        word_success = []

        # 将结果保存到列表中
        def save_result(p):
            try:
                word, entry, err = p
                if err:
                    # 超过5次
                    if self.word_retry[word] > 1:
                        words.remove(word)
                        self.word_list.append(word) # 加到尾部, 再次尝试.
                    self.word_retry[word] += 1
                    pass
                else:
                    self.downloaded += 1

                    words.remove(word)
                    word_success.append([word, entry])
            except Exception as e:
                pass

        for word in words:
            self.pool.apply_async(self.get_wiki_json, args=(word,), callback=save_result)

        request_begin = time.time()
        # 等待结束
        timeout=60*(len(words)/200)
        if timeout < 60 : timeout = 60
        timeout =60

        is_empty = self.pool.join(timeout=timeout)
        self.pool.kill()

        request_end = time.time()
        request_time_spent = round(request_end - request_begin, 2)

        # 保存文件
        for word_info in word_success:
            word = word_info[0]
            entry = word_info[1]
            if word == 'aux':
                continue
            fw = open("d:\\enwiktionary\\"+self.json_output_path+"\\"+word+".html", 'w', -1, encoding="utf_8_sig")
            fw.write(entry.decode("utf-8"))
            fw.close()

        io_end = time.time()
        io_time_spent = round( io_end - request_end , 2)

        timeout_str = "\ttime out..." if not is_empty else ""

        print(str(self.process_seq)+\
              "\tdownloaded: "+str(self.downloaded) +\
              "\tproxy: "+ str(len(self.proxy_list)) +\
              "\trequest time: "+ str(request_time_spent) +\
              "\tio time: "+ str(io_time_spent) +\
              timeout_str )

    #==-------------------------------------------------------
    # 获取一个成功过的代理
    def next_proxy(self):
        # 因为删除的原因
        if self.proxy_anchor >= len(self.proxy_list):
            self.proxy_anchor = 0

        proxy = self.proxy_list[self.proxy_anchor]
        self.proxy_anchor += 1

        return proxy

    def load_proxies(self, input_proxies_file):
        for proxy_file in input_proxies_file:
            if proxy_file and os.path.exists(proxy_file):
                with open(proxy_file) as fd:
                    for line in fd:
                        try:
                            j = json.loads(line)
                            j['failure'] = 0
                            j['success'] = 0
                            j['request'] = 0
                            j['refused'] = 0

                            type_= j['type']
                            host = j['host']
                            port = j['port']
                            proxy_hash = '%s:%s:%s' % (type_, host, port)
                            if proxy_hash in self.proxies_hash:
                                continue
                                
                            if type_ == 'http':
                                continue

                            self.proxy_list.append(j)
                        except Exception as e:
                            logger.info("[-] error: %s" % ( str(e)))


    def dump_proxies_info(self):
        for proxy in self.proxy_list:
            pass

    def process_proxies_info(self, proxy, test_info):

        if test_info.get('request'):
            # 代理的请求+1
            proxy['request'] += 1
        elif test_info.get('success'):
            proxy['success'] += 1
            proxy['failure'] = 0 # 成功过一次, 将其归零. 说明这个代理是正常的.
            proxy['refused'] = 0
        elif test_info.get('failure'):
            proxy['failure'] += 1
            # 如果代理连续5次连接不上, 将其删除掉
            if proxy['failure'] > 1:
                self.proxy_list.remove(proxy)
        elif test_info.get('refused'):
            proxy['refused'] += 1
            if proxy['refused'] > 10:
                self.proxy_list.remove(proxy)

    #==-------------------------------------------------------

    def load_downloaded_word_list(self):
        self.downloaded_word_list = {}
        
        downloaded_file = "d:\\enwiktionary\\downloaded.txt"
        #if not os.path.exists(downloaded_file):
        #    f = open(downloaded_file, 'w', -1, encoding="utf_8_sig")
        #    for fpath in glob.glob("d:\\enwiktionary\\*\\*.json"):
        #        m = re.search("([^\\\\]+)[.]json", fpath)
        #        fn = m.group(1)
        #        fn=fn.strip()
        #        f.write(fn+"\n")
        #    f.close()
        #    raise Exception("create download list.................")
        #else:
        if True:
            # 加载已经的下载单词列表
            f = open(downloaded_file, 'r', -1, encoding="utf_8_sig")
            for word in f:
                word = word.replace("\n","")
                word = word.strip()
                self.downloaded_word_list[word] = True
            f.close()

    def load_word_list(self):
        # 先加载已经下载的单词列表
        self.load_downloaded_word_list()

        fd_word_list    = open("d:\\enwiktionary-latest-all-titles-in-ns0-filted.txt", 'r', -1, encoding="utf_8_sig")
        for line in fd_word_list:
            line = line.replace("\n", "")
            word = line.strip()

            # 该单词还没有下载
            if len(word) > 0 and self.downloaded_word_list.get(word) is None:
                self.word_list.append(word)

        fd_word_list.close()
        
        print("undownloaded: "+str(len(self.word_list)) +"\tdownloaded: "+ str(len(self.downloaded_word_list)) )
        
        # 在多进程下面, 只检测部分
        if self.process_count > 1:
            num_per_part = int((len(self.word_list)+self.process_count-1)/self.process_count)
            start = self.process_seq*num_per_part
            end   = (self.process_seq+1)*num_per_part
            self.word_list = self.word_list[start:end]

            print("downloading range( {0}, {1} ), total number: {2}".format(start, end, len(self.word_list)))

    def start(self):
        cur_word_list = []

        while len(self.word_list) and len(self.proxy_list):

            # 每次1000个批量查询
            num = min(400-len(cur_word_list), len(self.word_list))
            for i in range(0, num):
                word = self.word_list.pop()
                cur_word_list.append(word)
                self.word_retry[word] = 0

            # 去下载这批数据
            self.batch_download_words(cur_word_list)

@click.command()
@click.argument('process_seq')
def main(process_seq):
    
    time.sleep(int(process_seq)*30)
    
    process_count = 6
    
    fs = []
    fs += glob.glob("x_valid_proxies*.txt")
    v = WiktionaryCrawler(fs, "20200210-00-"+str(process_seq), int(process_seq), process_count)
    v.start()

if __name__ == '__main__':
    main()



