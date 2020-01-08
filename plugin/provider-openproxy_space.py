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

# TODO: 好像被保护了, 不能获取
class Proxy(ProxyWithWebdriver):

    def __init__(self):
        urls = 'https://openproxy.space/list'
        super().__init__(urls, time_load_page=30, mode='multilink')
        
    def move_mouse_then_click(self):
        action_chains = ActionChains(self.driver)
        action_chains.key_down(Keys.PAGE_DOWN ).key_up(Keys.PAGE_DOWN).key_down(Keys.PAGE_DOWN ).key_up(Keys.PAGE_DOWN).perform()
        action_chains.reset_actions()
        action_chains = None
        time.sleep(10)
        
    def all_links(self, driver):
        # <a href="/list/lvMiLiX8PF" class="list http" rel="nofollow">
        #<div title="FRESH HTTP/S" class="title">
        # <span>FRESH HTTP/S</span></div> <div class="protocols"><div class="protocol">http</div><div class="protocol">https</div></div> <div class="count">5856</div> <div class="bot"><div class="date">6 hours ago</div> <div class="timeout">10s</div> <!----></div></a>
        
        html = self.driver.page_source
        #print(html)
        link_list = driver.find_elements_by_class_name('http')
        link_list += driver.find_elements_by_class_name('socks')
        #count = 10
        #while not link_list:
        #    count -=1
        #    if count == 0 : return # 退出吧
        #    driver.refresh()
        #    time.sleep(5)
        #    link_list = driver.find_elements_by_class_name('list http')
            
        #print(link_list)
        
        return link_list
        

if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)