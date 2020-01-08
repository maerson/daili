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
        urls = ['https://raw.githubusercontent.com/dxxzst/free-proxy-list/master/README.md']
        super().__init__(urls, time_load_page=20)

    def driver_copy(self, url):
        html = self.driver.page_source
        self.driver.close()

        soup = BeautifulSoup(html, "lxml")
        text = soup.find("body").text

        # |62.210.105.103|3128|https|low|France|
        proxy_list = re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\|](\d+)", text)
        self.result.extend([{'host': host, 'port': int(port), 'from': 'dxxzst'} for host, port in proxy_list])

if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)