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
        urls = 'https://listproxy.net/' 
        super().__init__(urls, time_load_page=30, mode = 'multilink',  )
        
    def visit_link(self, driver, url, cur_page_num ):
        re_ip_port_result = []
        count = 7
        # <h2 class="entry-title"><a href="https://listproxy.net/2019/11/30/free-proxy-server-list-18/" rel="bookmark">30-11-19 | Free Proxy Server List (4652)</a></h2>
        link_list = driver.find_elements_by_xpath('//h2[@class="entry-title"]/a')
        while not link_list:
            count -=1
            if count == 0 : return # 退出吧
            driver.refresh()
            time.sleep(5)
            link_list = driver.find_elements_by_xpath('//h2[@class="entry-title"]/a')

        if cur_page_num < len(link_list):
            link = link_list[cur_page_num]
            link.click()
            #print(str(link))
            
            self.driver_copy(url)

            # 回退到主页
            driver.back()
            
            if cur_page_num >= len(link_list): return None
            return cur_page_num + 1
            
        else:
            return None
            
if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)

