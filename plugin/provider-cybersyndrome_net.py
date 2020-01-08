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
        urls = 'http://www.cybersyndrome.net/pla6.html'
        super().__init__(urls, time_load_page=30)#, multi_page='Y' 
            
if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)