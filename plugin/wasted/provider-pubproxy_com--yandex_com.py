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

    def extract_proxy(self):
    
        options = webdriver.FirefoxOptions()
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Firefox(firefox_options=options, proxy=None)

        driver.minimize_window()
        # driver.set_window_size(800,600)
        # driver.set_window_position(0,0)
        driver.get('https://translate.yandex.com/translate')

        #driver.implicitly_wait(15)
        time.sleep(10)
        # <input id="urlInput" type="text" class="textinput" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" placeholder="Enter a website address">
        # <span class="button" data-action="submitUrl">Translate</span>
        url_form = driver.find_element_by_id('urlInput')
        submit_button = driver.find_element_by_xpath('//span[@data-action="submitUrl"]')

        url_form.click()
        url_form.send_keys('http://pubproxy.com/api/proxy?limit=5&format=txt&type=http&level=anonymous&last_check=60&no_country=CN')
        submit_button.click()

        # 需要从这个iframe中获取代理IP
        driver.switch_to_frame("targetFrame")

        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.XPATH,"//body/pre")))

        # 从网页中提取IP
        html = driver.page_source
        driver.close()

        re_ip_port_result = []
        proxy_list = re.findall('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):([\d]{1,5})', html)
        re_ip_port_result.extend([{'host': host, 'port': int(port), 'from': 'http://pubproxy.com'} for host, port in proxy_list])
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