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
from lxml import etree

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

    def start(self):

        options = webdriver.FirefoxOptions()
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Firefox(firefox_options=options, proxy=None)

        #driver.minimize_window()
        # driver.set_window_size(800,600)
        # driver.set_window_position(0,0)
        driver.get('https://translate.yandex.com/translate')

        #driver.implicitly_wait(15)
        time.sleep(3)
        # <input id="urlInput" type="text" class="textinput" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" placeholder="Enter a website address">
        # <span class="button" data-action="submitUrl">Translate</span>
        url_form = driver.find_element_by_id('urlInput')
        submit_button = driver.find_element_by_xpath('//span[@data-action="submitUrl"]')

        url_form.click()
        url_form.send_keys('https://www.proxynova.com/proxy-server-list/')
        submit_button.click()

        # 需要从这个iframe中获取代理IP
        driver.switch_to_frame("targetFrame")

        WebDriverWait(driver, timeout=120).until(EC.presence_of_element_located((By.XPATH,"//tr[@data-proxy-id]")))

        # 从网页中提取IP
        html = driver.page_source

        re_ip_port_result = []

        # <td align="left" onclick="javascript:check_proxy(this)">
        #   <abbr title="89-28-164-55.cable.mart.ru"><script>document.write('1234567889.28'.substr(8) + '.164.55');</script> </abbr>
        # </td>
        #   <td align="left">
        #             <a href="https://z5h64q92x9.net/proxy_u/en-zh.en/https/www.proxynova.com/proxy-server-list/port-8080/" title="Port 8080 proxies">8080</a>
        #             </td>
        # <tr data-proxy-id="1521475">

        html_dom = etree.HTML(html)
        proxy_tr_list = html_dom.xpath("//tr[@data-proxy-id]")
        for proxy_tr in proxy_tr_list:
            innerText = etree.tostring(proxy_tr).decode('utf-8')

            groups = re.findall(r"document\.write\('12345678(\d{1,3}\.\d{1,3})'\.substr\(8\) \+ '(\d{1,3}\.\d{1,3}\.\d{1,3})'\)", innerText)
            port   = re.search(r">\s*(\d{1,5})\s*<", innerText)

            if groups and len(groups) > 0 and len(groups[0]) > 0 :
                host = groups[0][0] + groups[0][1]
                re_ip_port_result.extend([{'host': host, 'port': port.group(1), 'from': 'https://www.proxynova.com'}])

        self.result.extend(re_ip_port_result)

        driver.close()

if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)