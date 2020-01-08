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
        urls = [ 'https://api.proxyscrape.com/?request=share&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all'
                ,'https://api.proxyscrape.com/?request=share&proxytype=socks4&timeout=10000&country=all'
                ,'https://api.proxyscrape.com/?request=share&proxytype=socks5&timeout=10000&country=all'
        ]
        super().__init__(urls, time_load_page=30, multi_page='Y', max_pagenum=20 )
        
    def move_mouse_then_click(self):
        action_chains = ActionChains(self.driver)
        action_chains.move_by_offset(500, 500)
        action_chains.click()
        action_chains.reset_actions()
        action_chains = None
            
if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)