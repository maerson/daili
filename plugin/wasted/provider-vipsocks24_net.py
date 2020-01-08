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
        urls = 'http://www.vipsocks24.net/'
        super().__init__(urls, time_load_page=30, mode='multilink', linktext='Read more')

if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)