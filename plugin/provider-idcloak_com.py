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
        # http://www.idcloak.com/proxylist/free-proxy-ip-list.html
        urls = 'http://www.idcloak.com/proxylist/proxy-list.html'
        super().__init__(urls, time_load_page=30, multi_page='Y')
        
    def parse_ip_port(self, url, text):
        re_ip_port_encode_result = None

        if self.pattern is None:
            re_ip_port_encode_result  = re.findall("(\d{1,5})\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text, re.M)
            re_ip_port_encode_result += re.findall("(\d{1,5}):(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text, re.M)
        else:
            re_ip_port_encode_result  = re.findall(self.pattern, text, re.M)

        netloc = self.base_url(url)
        # 适用于web http 代理的情况下
        if self.from_ : netloc = self.from_

        return [{'host': ip, 'port': int(port) , 'from': netloc } for port,ip in re_ip_port_encode_result]

    def next_page(self, pagenum):
        try:
            # 下一页
            #<input type="submit" style="width:30px; height:25px" name="page" value="2">
            self.driver.find_element_by_xpath('//input[@value="'+str(pagenum+1) +'"]').click()
            #self.driver.find_element_by_link_text(str(pagenum+1)).click()
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

