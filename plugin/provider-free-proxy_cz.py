from __future__ import unicode_literals, absolute_import, division, print_function
import json
import re
import logging
import os, sys, time


if __name__ == '__main__':
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    sys.path.append(sys.path[0]+"\\plugin")

from provider import *

# TODO: 需要后续处理, 太耗时间
class Proxy(ProxyWithWebdriver):
    def __init__(self):
        urls = [ 'http://free-proxy.cz/en/proxylist/main/{}'.format(i) for i in range(1, 10) ]
        super().__init__(urls, time_load_page=20 )


if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
 
