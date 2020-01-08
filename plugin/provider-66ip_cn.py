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
        urls = [ "http://www.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=".format(300) ] +\
               [ "http://www.66ip.cn/nmtq.php?getnum={}&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip".format(300)]
        super().__init__(urls, time_load_page=40)


if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)


