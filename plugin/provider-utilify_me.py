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
        urls = 'https://utilify.me/proxy-list'
        super().__init__(urls, time_load_page=30 )
        
    def driver_get(self, url):
        # html = driver.execute_script("return document.documentElement.outerHTML")
        try:
            self.driver.get(url )
            self.driver.set_window_size(100,80)
            self.driver.set_window_position(-200,-200)
            #self.driver.minimize_window()
            # WebDriverWait(driver, timeout=30).until(dom_is_rewritten(pattern))
            #
            # b.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.time_load_page)
            
            #<button class="show-more">Show More</button>
            count = 6
            while count:
                # 被网站屏蔽掉了!!!!
                self.driver.find_element_by_xpath('//button[@class="show-more"]').click()
                count -= 1
                time.sleep(2)
            
        except Exception as e:
            self.logger.info("[-] get() error: %s" % ( str(e)))
            pass
            
if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)