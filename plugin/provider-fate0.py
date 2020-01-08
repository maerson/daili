from __future__ import unicode_literals, absolute_import, division, print_function
import json
import re
import logging
import os, sys, time
from bs4 import BeautifulSoup

if __name__ == '__main__':
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    sys.path.append(sys.path[0]+"\\plugin")

from provider import *

"""
https://www.youneed.win/proxy
这个网站每天都更新proxy list, 以及SS账号
"""

class Proxy(ProxyWithWebdriver):

    def __init__(self):
        urls = ['https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list']
        super().__init__(urls, time_load_page=20)

    def driver_copy(self, url):
        html = self.driver.page_source
        self.driver.close()

        soup = BeautifulSoup(html, "lxml")
        text = soup.find("body").text

        # |62.210.105.103|3128|https|low|France|
        for line in text.split("\n"):
            if len(line.strip()) < 1: continue
            obj = json.loads(line)
            self.result.extend([{'host': obj['host'], 'port': obj['port'], 'from': 'fate0'} ])

if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
