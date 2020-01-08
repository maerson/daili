from __future__ import unicode_literals, absolute_import, division, print_function
import json
import re
import time
import base64
import logging
import retrying
import requests
import time
import os, sys, time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip

class Proxy(object):
    def __init__(self):
        self.url = 'http://www.sslproxies24.top/'
        self.result = []


    def extract_proxy(self, url) :
        

        options = webdriver.FirefoxOptions()
        options.add_argument('--ignore-certificate-errors')
        #options.add_argument('--headless') # 不打开GUI窗口
        #options.add_argument('--browser')
        #options.add_argument('--private')
        #options.add_argument('-url "https://free-ss.site/"')
        #options.add_argument('-P "Profile0"') # -profile "profile_path"
        driver = webdriver.Firefox(firefox_options=options, proxy=None)
        #driver.set_page_load_timeout(20)
        driver.get(url )
        time.sleep(30)
        
        nextpage = 0 
        while nextpage is not None:
            nextpage = self.visit_subpage(driver, nextpage)

        driver.delete_all_cookies()
        driver.close()
        driver = None
    
    def visit_subpage(self, driver, cur_page_num ):
        re_ip_port_result = []
        count = 7
        link_list = driver.find_elements_by_partial_link_text('Read more')
        while not link_list:
            count -=1
            if count == 0 : return # 退出吧
            driver.refresh()
            time.sleep(5)
            link_list = driver.find_elements_by_partial_link_text('Read more')

        if cur_page_num < len(link_list):
            link = link_list[cur_page_num]
            link.click()
            #print(str(link))
            
            time.sleep(2)
            #print("before .....")
            # 拷贝文档
            action_chains = ActionChains(driver)
            driver.find_element_by_xpath('//body').click()
            #Ctrl-a
            action_chains.key_down(Keys.LEFT_CONTROL).send_keys("a").key_up(Keys.LEFT_CONTROL).perform()
            action_chains.reset_actions()
            action_chains = None
            #print("ctrl+a .....")
            time.sleep(2)

            #Ctrl-c
            action_chains = ActionChains(driver)
            action_chains.key_down(Keys.LEFT_CONTROL).send_keys("c").key_up(Keys.LEFT_CONTROL).perform()
            action_chains.reset_actions()
            action_chains = None
            #print("ctrl+c .....")
            time.sleep(2)
            

            text = pyperclip.paste()
            
            re_ip_port_encode_result  = re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\d{1,5})", text, re.M)
            re_ip_port_encode_result += re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})", text, re.M)
            re_ip_port_result.extend([{'host': ip, 'port': int(port) , 'from': 'http://www.sslproxies24.top/'} for ip, port in re_ip_port_encode_result])
            
            #print(str(re_ip_port_result))
            self.result.extend(re_ip_port_result)
            # 回退到主页
            driver.back()
            time.sleep(5)
            
            if cur_page_num >= len(link_list): return None
            return cur_page_num + 1
            
        else:
            return None
            

    def start(self):
        self.extract_proxy(self.url)


if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
