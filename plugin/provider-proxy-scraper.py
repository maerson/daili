from __future__ import unicode_literals, absolute_import, division, print_function
import json
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
from bs4 import BeautifulSoup

class Proxy(object):
    def __init__(self):
        self.url = 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.json'
        self.result = []

    def extract_proxy(self) :
        re_ip_port_result = []
        
        #headers = {
        #        'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) "
        #                      "Chrome/21.0.1180.89 Safari/537.1'"
        #    }
        #rp = requests.get(self.url, timeout=20, headers=headers)
        #print("1")
        options = webdriver.FirefoxOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless') # 不打开GUI窗口
        driver = webdriver.Firefox(firefox_options=options, proxy=None)
        driver.get(self.url )
        time.sleep(10)
        html = driver.page_source
        driver.close()
        
        soup = BeautifulSoup(html, "lxml")
        obj = json.loads(soup.find("body").text)

        #obj = json.loads(dict_from_json)
        if not obj: return 
        if obj['proxynova']:
            for item in obj['proxynova']:
                host = item['ip']
                port = item['port']
                re_ip_port_result.extend([{'host': host, 'port': port, 'from': 'proxy-scraper'} ])
        
        if obj['usproxy']:
            for item in obj['usproxy']:
                host = item['ip']
                port = item['port']
                re_ip_port_result.extend([{'host': host, 'port': port, 'from': 'proxy-scraper'} ])
                
        self.result.extend(re_ip_port_result)

    def start(self):
        self.extract_proxy()
        
if __name__ == '__main__':
    p = Proxy()
    p.start()

    for i in p.result:
        print(i)
        