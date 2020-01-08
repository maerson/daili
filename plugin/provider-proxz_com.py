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


class Proxy(ProxyWithWebdriver):

    def __init__(self):
        urls = [ 'http://www.proxz.com/proxy_list_high_anonymous_0.html'
                ,'http://www.proxz.com/proxy_list_uk_0.html'
                ,'http://www.proxz.com/proxy_list_jp_0.html'
                ,'http://www.proxz.com/proxy_list_ca_0.html'
                ,'http://www.proxz.com/proxy_list_anonymous_us_0.html'
                ,'http://www.proxz.com/proxy_list_cn_ssl_0.html'
                ,'http://www.proxz.com/proxy_list_fr_0.html'
                ,'http://www.proxz.com/proxy_list_transparent_0.html'
                ,'http://www.proxz.com/proxy_list_port_std_0.html'
                ,'http://www.proxz.com/proxy_list_port_nonstd_0.html'
               ]
        super().__init__(urls, time_load_page=30, multi_page='Y')

if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
