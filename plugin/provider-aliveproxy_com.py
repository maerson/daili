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
        urls = [ 'http://aliveproxy.com/anonymous-proxy-list/', 
                 'http://aliveproxy.com/high-anonymity-proxy-list',
                 'http://aliveproxy.com/transparent-proxy-list',
                 'http://aliveproxy.com/socks5-list',
                 'http://aliveproxy.com/socks4-list'
        ]
        
        super().__init__(urls, time_load_page=20)#, multi_page='Y'


if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
