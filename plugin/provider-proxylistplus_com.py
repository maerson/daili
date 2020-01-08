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
        urls = 'https://list.proxylistplus.com'  
        super().__init__(urls, time_load_page=30, multi_page='Y' )
        
    def next_page(self, pagenum):
        try:
            # 下一页
            #<a href="?stype=1&amp;page=2">2</a>
            #driver.find_element_by_xpath('//li/a[contain(@href, "/en/proxy-list/?start=")]'+str(pagenum+1) +'"]/a').click()
            self.driver.find_element_by_link_text("["+str(pagenum+1)+"]").click()
            # 页数增加
            return pagenum+1
        except Exception as e:
            self.logger.info("[-] next_page() error: %s" % ( str(e)))
            pass
            
if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
