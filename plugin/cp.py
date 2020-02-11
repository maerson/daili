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
        self.num = 416
        urls = [ 'http://cqcounter.com/tags/proxy_{}.html'.format(self.num)]
        super().__init__(urls, time_load_page=30, multi_page='Y', max_pagenum=557, auto_proxy=False)#
        self.out_file = open("d:\\proxy_urls.txt", 'a', -1, encoding="utf_8_sig")
      
    def extract_proxy_multipages(self,url) :
        # 1) 初始化driver
        # 2) 打开其实url
        # 3) 获取内容, 并分析其中的ip:port
        # 4) 对于分页的, 进入下一页
        self.driver_setup(url)
        self.driver_get(url)

        pagenum = self.num
        while pagenum < self.max_pagenum:

            #拷贝网页的内容, 并分析其中的IP:PORT
            self.driver_copy(url)

            # 没有分页, 直接退出
            if self.multi_page is False:
                break
            else:
                pagenum = self.next_page(pagenum)
                if pagenum is None: break
                
    def driver_copy(self, url):
        try:
            # <span class="url">Proxy.net.pl</span>
            es = self.driver.find_elements_by_xpath('//span[@class="url"]')
            for url in es:
                #print("url: "+ url.get_attribute('innerHTML'))
                #print("url: "+ url.text)
                self.out_file.write(url.text+"\n")
                self.out_file.flush()
        except:
            pass

if __name__ == '__main__':
    p = Proxy()
    p.start()
    p.out_file.close()

    for i in p.result:
        print(i)
