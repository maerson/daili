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

class Proxy(ProxyWithWebdriver):

    def __init__(self):
        urls = [ 'https://github.com/clarketm/proxy-list/blob/master/proxy-list-raw.txt',
                    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                    'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
                    'https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt',
                    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
                    'https://raw.githubusercontent.com/h4mid007/free-proxy-list/master/proxies.txt',
        ]
        super().__init__(urls, time_load_page=40)


if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)

