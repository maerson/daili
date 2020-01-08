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
        urls = [ 'https://z5h64q92x9.net/proxy_u/en-zh.en/spys.one/en/free-proxy-list/',
                       'https://z5h64q92x9.net/proxy_u/en-zh.en/spys.one/en/free-proxy-list/1/',
                       'https://z5h64q92x9.net/proxy_u/en-zh.en/spys.one/en/free-proxy-list/2/' ]
        super().__init__(urls, time_load_page=30, iframe="targetFrame", from_= 'http://spys.one')

if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)

