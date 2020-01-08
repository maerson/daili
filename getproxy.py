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

if __name__ == '__main__':
    sys.path.append(os.path.dirname(sys.path[0]))
    sys.path.append(os.path.dirname(sys.path[0])+"/plugin")


from utils import signal_name, load_object

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class GetProxy(object):
    base_dir = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, input_proxies_file=None, output_proxies_file=None, retry=False):
        self.pool = gevent.pool.Pool(500)
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

        self.outfile = open(output_proxies_file+"_"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".txt", 'w', -1, "utf-8")


    if "从网络上抓取代理列表":
        def load_plugins(self):
            logger.info("[*] Load plugins")
            #print(str(self.retry_plugin_list))
            
            loaded = True
            for plugin_name in os.listdir(os.path.join(self.base_dir, 'plugin')):
                if not re.match( "^provider[-].+[.]py",plugin_name):
                    continue
                
                if False:
                   # 加载某个插件以后
                   if re.search("proxyhttp_net",plugin_name): 
                       loaded = False
                       continue
                   if loaded is True: 
                       continue

                # 需要重试
                if len(self.retry_plugin_list) and self.retry_plugin_list.get(plugin_name) is None:
                    continue

                try:
                    cls = load_object("plugin.%s.Proxy" % os.path.splitext(plugin_name)[0])
                    logger.info("[*] Loaded plugin %s" % plugin_name)
                except Exception as e:
                    logger.info("[-] Load Plugin %s error: %s" % (plugin_name, str(e)))
                    continue

                inst = cls()
                inst.proxies = copy.deepcopy(self.valid_proxies)
                self.plugins[plugin_name] = { 'inst': inst , 'count': 0 }

        # 通过协程, 快速抓取
        def grab_web_proxies(self):
            logger.info("[*] Grab proxies")

            for plugin_name, plugin_info in self.plugins.items():
                #self.pool.spawn(plugin.start)
                try:
                    try:
                        plugin_info['inst'].set_logger_prefix(plugin_name)
                    except:
                        pass
                    plugin_info['inst'].start()
                    plugin_info['count'] += len(plugin_info['inst'].result)

                    if  plugin_info['inst'].result and len( plugin_info['inst'].result):
                        self.save_proxies(plugin_info['inst'].result)
                except Exception as e:
                    logger.info("[-] Start crawling error: %s" % ( str(e)))

            #self.pool.join(timeout=8 * 60)
            #self.pool.kill()

        def validate_web_proxies(self, web_proxies):
            logger.info("[*] Validate web proxies")
            input_proxies_len = len(self.proxies_hash)

            valid_proxies = self._validate_proxy_list(web_proxies)
            self.valid_proxies.extend(valid_proxies)

            output_proxies_len = len(self.proxies_hash) - input_proxies_len

            logger.info("[*] Check %s output proxies, Got %s valid output proxies" % (output_proxies_len, len(valid_proxies)))
            logger.info("[*] Check %s proxies, Got %s valid proxies" % (len(self.proxies_hash), len(self.valid_proxies)))


    def save_proxies(self, valid_proxies):
        for item in valid_proxies:
            self.outfile.write("%s\n" % json.dumps(item))
            self.outfile.flush()

    def dump_stats(self):
        logger.info("[*]=====================================")
        for plugin_name, plugin_info in self.plugins.items():
            logger.info("[*] %s : %s " % (plugin_name, plugin_info['count']))

        logger.info("[*]=====================================")
    def start(self):
        # 1) 检查历史数据
        #self.validate_input_proxies()
        # 2) 抓取
        self.load_plugins()
        self.grab_web_proxies()
        #self.validate_web_proxies()
        # 3) 保存结果
        self.outfile.close()
        self.dump_stats()



if __name__ == '__main__':
    g = GetProxy("","web_proxies") #, True
    g.start()



