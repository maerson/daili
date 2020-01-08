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
        urls =  'https://www.proxy-list.download/HTTP'
        super().__init__(urls, time_load_page=30, multi_page='Y' )
        
    def next_page(self, pagenum):
        try:
            self.driver.find_element_by_xpath('//a[@id="btn2"]').click()
            # 页数增加
            return pagenum+1
        except Exception as e:
            self.logger.info("[-] next_page() error: %s" % ( str(e)))
            return None
            
if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
