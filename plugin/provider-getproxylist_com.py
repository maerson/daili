from __future__ import unicode_literals, absolute_import, division, print_function
import json
import re
import time
import base64
import logging
import retrying
import requests
import time
import os, sys, time
import re
from bs4 import BeautifulSoup

class Proxy(object):
    def __init__(self):
        self.url = 'https://api.getproxylist.com/proxy?protocol[]=http'
        self.result = []

    def extract_proxy(self) :
        try:
            request_proxies = {
                'https': "%s:%s" % ("127.0.0.1", 1082)
            }
            response_json = requests.get(self.url, proxies=request_proxies, timeout=5).json()
            host=response_json.get('ip', "")
            port=response_json.get('port', "")
            self.result.extend([{'host': host, 'port': port, 'from': 'https://api.getproxylist.com'} ])
        except Exception as e:
            print(str(e))
            return
            
        

    def start(self):
        self.extract_proxy()
        
if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
        