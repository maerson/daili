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

# 这个网站防采集.
#
#
class Proxy(ProxyWithWebdriver):

    def __init__(self):
        urls = [ 'https://proxydb.net/']
        super().__init__(urls, time_load_page=30, multi_page='Y')
        
    def next_page(self, pagenum):
        try:
            # 下一页
            #<a href="#" class="page-link">Next page<i class="fa fa-fw fa-arrow-right"></i></a>
            #driver.find_element_by_xpath('//li/a[contain(@href, "/en/proxy-list/?start=")]'+str(pagenum+1) +'"]/a').click()
            self.driver.find_element_by_link_text('Next page').click()
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
