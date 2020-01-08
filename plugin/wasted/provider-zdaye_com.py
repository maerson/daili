#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function

import re
import time
import base64
import logging
import retrying
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os, sys, time
import re

logger = logging.getLogger(__name__)

class dom_is_rewritten(object):
    """An expectation for checking that an element has a particular css class.
    locator - used to find the element
    returns the WebElement once it has the particular css class
    """
    def __init__(self):
        #self.locator = locator
        #self.cond_str = cond_str
        pass
    
    def __call__(self, driver):
        html = driver.page_source
        proxy_list = re.findall('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):([\d]{1,5})', html)
        if len(proxy_list): return True
        else: return False
        
class Proxy(object):
    def __init__(self):
        self.cur_proxy = None
        self.proxies = []
        self.result = []

    def extract_proxy(self) :
        options = webdriver.FirefoxOptions()
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Firefox(firefox_options=options, proxy=None)
        driver.get('https://www.zdaye.com/dayProxy.html')
          
        # 等待javascript 重写DOM完毕
        e = WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH,"//a[starts-with(@href,/dayProxy/ip)]")))
        
        # 这时获得的html内容是正确的
        html = driver.page_source
        driver.close()
        
        subpages = re.findall('href="/dayProxy/ip/(\d+).html"', html)
        re_ip_port_result = []
        for page_num in subpages:
            try:
                url = "https://www.zdaye.com/dayProxy/ip/{}.html".format(page_num)
                driver = webdriver.Firefox(firefox_options=options, proxy=None)
                driver.get(url)
                e = WebDriverWait(driver, timeout=10).until(dom_is_rewritten())
                html = driver.page_source
                driver.close()
                
                proxy_list = re.findall('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):([\d]{1,5})', html)
                
                re_ip_port_result.extend([{'host': host, 'port': int(port), 'from': 'https://www.zdaye.com'} for host, port in proxy_list])

            except:
                pass

        self.result.extend(re_ip_port_result)

    def start(self):
        try:
            self.extract_proxy()
        except:
            pass

if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)