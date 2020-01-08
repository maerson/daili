#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function, absolute_import

#import gevent.monkey
#gevent.monkey.patch_all()

import os, sys, time, re, math, random, logging
import click
import copy
import geoip2.database
import json
import multiprocessing
import queue
import requests
import signal
import urllib.request

from collections import OrderedDict
from datetime import datetime
from importlib import import_module
from importlib import import_module
from lxml import etree
from multiprocessing import Process, Pool, TimeoutError, Queue
from requests.models import Response
from time import sleep


if __name__ == '__main__':
    sys.path.append(os.path.dirname(sys.path[0]))
    sys.path.append(os.path.dirname(sys.path[0])+"/plugin")


from utils import signal_name, load_object

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def fetch_proxies(plugin_path, lock, outfile_path):#
    try:
        cls = load_object("plugin.%s.Proxy" % os.path.splitext(plugin_path)[0])
        print("[*] Loaded plugin %s" % plugin_path)
        inst = cls()
        inst.setLock(lock)
        inst.start()

        if lock: lock.acquire()
        try:
            outfile = open(outfile_path, 'a', -1, "utf-8")
            for item in inst.result:
                outfile.write("%s\n" % json.dumps(item))
            outfile.close()    
        finally:
            if lock: lock.release()
        

    except Exception as e:
        print("[-] Load Plugin %s error: %s" % (plugin_path, str(e)))


def error_callback(e):
    logger.info("[-] fetch_proxies error: %s" % (str(e)))

class GetProxy(object):
    base_dir = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, input_proxies_file=None, output_proxies_file=None, retry=False):
        #self.pool = gevent.pool.Pool(500)
        self.plugins = OrderedDict()
        self.valid_proxies = []
        self.input_proxies_file = input_proxies_file
        self.proxies_hash = {}
        self.plugin_info = dict()
        self.retry_plugin_list = dict()
        if retry:
            with open("stats.txt") as fd:
                for line in fd:
                    m = re.search("(?P<name>provider[^:]+) : 0", line)
                    if m:
                        self.retry_plugin_list[m.group('name')] = []

        self.outfile = output_proxies_file+"_"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".txt"


    if "从网络上抓取代理列表":
        def load_plugins(self):
            logger.info("[*] Load plugins")

            for plugin_name in os.listdir(os.path.join(self.base_dir, 'plugin')):
                if not re.match( "^provider[-].+[.]py",plugin_name):
                    continue

                # 需要重试
                if len(self.retry_plugin_list) and self.retry_plugin_list.get(plugin_name) is None:
                    continue

                self.plugins[plugin_name] = { 'count': 0 }
                #logger.info("[*] Found plugin %s" % plugin_name)

        # 通过协程, 快速抓取
        def grab_web_proxies(self):
            logger.info("[*] Grab proxies")

            proxy_q = multiprocessing.Manager().Queue()
            lock = multiprocessing.Manager().Lock()

            keys = [k for k,v in self.plugins.items()]
            thread_count = 5

            mp_pool = Pool(thread_count)
            try:
                for i in range(0, len(self.plugins)):
                    mp_pool.apply_async(fetch_proxies, args=(keys[i], lock, self.outfile,), error_callback=error_callback)
                mp_pool.close()
                mp_pool.join()
            except Exception as e:
                logger.info("[-] Run error: %s" % (str(e)))


    def dump_stats(self):
        logger.info("[*]=====================================")
        for plugin_name, plugin_info in self.plugins.items():
            logger.info("[*] %s : %s " % (plugin_name, plugin_info['count']))

        logger.info("[*]=====================================")
        
    def start(self):
        self.load_plugins()
        self.grab_web_proxies()


if __name__ == '__main__':
    g = GetProxy("","web_proxies") #, True
    g.start()



