#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function

import os, sys
import re
import logging
import retrying
import requests

import re
import time
import base64
import logging
import retrying
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os, sys, time
import re

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    sys.path.append(sys.path[0]+"\\plugin") 

from provider import *


simple_provider_info = [
    {
        'url_list' : [
                    'http://comp0.ru/downloads/proxylist.txt',
                    'http://www.atomintersoft.com/anonymous_proxy_list',
                    'http://www.atomintersoft.com/high_anonymity_elite_proxy_list',
        ],
        'pattern' : r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):([\d]{1,5})",
    },
    
    {
        'url_list' : [ 'http://ip.jiangxianli.com/?page={}'.format(i) for i in range(1, 5) ],
        'pattern'  : r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>',
    },


]

class Proxy(ProxyProvider):
    def __init__(self):
        self.result = []

    def extract(self, url, pattern):
        try:
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) "
                              "Chrome/21.0.1180.89 Safari/537.1'"
            }
            rp = requests.get(url, headers=headers, timeout=10)
            sleep(20)
            #print(rp.text)

            re_ip_port_result = re.findall(pattern, rp.text)

            if not re_ip_port_result:
                raise Exception("empty")

        except Exception as e:
            logger.error("[-] Request url {url} error: {error}".format(url=url, error=str(e)))
            return []

        return [{'host': host, 'port': int(port), 'from': 'txt'} for host, port in re_ip_port_result]


    def start(self):
        for entry in simple_provider_info:
            url_list = entry['url_list']
            pattern  = entry['pattern']
            for url in url_list:
                #if re.search("www.free-proxy-list.net", url) is None: continue
                #print("*** " + str(url) + "\t" + str(pattern))
                re_ip_port_result = self.extract(url, pattern)
                self.result.extend(re_ip_port_result)
                time.sleep(10)

if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)

    print(len(p.result))
