#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function, absolute_import

import gevent.monkey
gevent.monkey.patch_all()

import os
import sys
import json
import time
from datetime import datetime
import copy
import signal
import logging
import math
import re
import random
import requests
import gevent.pool
import geoip2.database
import click
from importlib import import_module
from lxml import etree
from requests.models import Response
from time import sleep
import urllib.request
from importlib import import_module
from collections import OrderedDict

import itertools
import json
import re
import sys
import time
import glob
import html2text
import requests
from pyquery import PyQuery as pq

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# This code uses the Wiktionary REST API to retrieve definitions and transform them into a format more like that which is used by Wordnik.

class WiktionaryCrawler:

    def __init__(self, input_proxies_file):
        self.fd_badword_list = open("d:\\enwiktionary\\not_english_wordlist.txt", 'w', -1, encoding="utf_8_sig")

        self.pool = gevent.pool.Pool(500)
        self.word_list = []
        self.input_proxies_file = input_proxies_file
        self.proxy_anchor = 0
        self.proxy_list = []
        self.downloaded = 0
        self.word_retry = {}
        self.proxies_hash = {}

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
                scheme = 'http'
            
            url = "%s://en.wiktionary.org/api/rest_v1/page/definition/"  % (scheme)
            r = requests.get( url + word,proxies=request_proxies, timeout=20, verify=False)
            # 成功
            if r.status_code is 200:
                self.process_proxies_info(proxy, { 'success': '1' })
                return (word, r.json(), None)
            else:
                return (word, None, r.status_code)
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
                    if self.word_retry[word] > 3:
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
        timeout =40
        
        is_empty = self.pool.join(timeout=timeout)
        self.pool.kill()
        
        request_end = time.time()
        request_time_spent = round(request_end - request_begin, 2)


        # 保存文件
        for word_info in word_success:
            word = word_info[0]
            entry = word_info[1]
            fw = open("d:\\enwiktionary\\20191230\\0\\"+word+".json", 'w', -1, encoding="utf_8_sig")
            fw.write(json.dumps(entry, indent=4))
            fw.close()
        
        io_end = time.time()        
        io_time_spent = round( io_end - request_end , 2)
        
        timeout_str = "\ttime out..." if not is_empty else ""
        
        print("downloaded: "+str(self.downloaded) +\
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

    def load_proxies(self):
        for proxy_file in self.input_proxies_file:
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
                            proxy_hash = '%s:%s' % (host, port)
                            if proxy_hash in self.proxies_hash:
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
            if proxy['failure'] > 2:
                self.proxy_list.remove(proxy)
        elif test_info.get('refused'):
            proxy['refused'] += 1
            if proxy['refused'] > 15:
                self.proxy_list.remove(proxy)

    #==-------------------------------------------------------

    def load_downloaded_word_list(self):
        self.downloaded_word_list = {}
        for fpath in glob.glob("d:\\enwiktionary\\*\\*.json"):
            #fn = os.path.basename(fpath)
            m = re.search("([^\\\\]+)[.]json", fpath)
            fn = m.group(1)
            self.downloaded_word_list[fn] = True
            #print(fn)

    def load_word_list(self):
        # 先加载已经下载的单词列表
        self.load_downloaded_word_list()

        fd_word_list    = open("d:\\enwiktionary-latest-all-titles-in-ns0-filted.txt", 'r', -1, encoding="utf_8_sig")
        #count = 0
        for line in fd_word_list:
            #count += 1
            ## 上次断在这里
            #if count < 5000: continue
            ## TODO: 暂时测试
            #if count > 10000: break
            word = line.strip()

            # 该单词还没有下载
            if len(word) > 0 and self.downloaded_word_list.get(word) is None:
                if re.search("^[a]", word):
                    self.word_list.append(word)

        fd_word_list.close()

    def start(self):
        self.load_proxies()
        self.load_word_list()
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

            #time.sleep(2)

    def cleanup(self):
        self.fd_badword_list.close()

if __name__ == '__main__':

    v = WiktionaryCrawler([ "d:\\proxy\\valid_proxies_2019-12-30-21-46-53.txt"])
    v.start()
    v.cleanup()


