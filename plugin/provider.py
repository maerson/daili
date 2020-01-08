from __future__ import unicode_literals, absolute_import, division, print_function

import base64
import copy
import json
import logging
import os, sys, time
import pyperclip
import random
import re
from time import sleep

import geoip2.database
import requests
import signal
import retrying
import urllib.request
from bs4 import BeautifulSoup
from lxml import etree
from requests.models import Response
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType
#from pyvirtualdisplay import Display
from urllib.parse import urlparse
# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) "
                  "Chrome/21.0.1180.89 Safari/537.1'"

}

# 'https://wtfismyip.com/text',
# 'http://api.ipify.org/',
# 'http://ipinfo.io/ip',
# 'http://ipv4.icanhazip.com/',
# 'http://myexternalip.com/raw',
# 'http://ipinfo.io/ip',
# 'http://ifconfig.io/ip',

def update_geoip_db():
    print('The update in progress, please waite for a while...')
    filename = 'GeoLite2-City.tar.gz'
    local_file = os.path.join(DATA_DIR, filename)
    city_db = os.path.join(DATA_DIR, 'GeoLite2-City.mmdb')
    url = 'http://geolite.maxmind.com/download/geoip/database/%s' % filename

    urllib.request.urlretrieve(url, local_file)

    tmp_dir = tempfile.gettempdir()
    with tarfile.open(name=local_file, mode='r:gz') as tf:
        for tar_info in tf.getmembers():
            if tar_info.name.endswith('.mmdb'):
                tf.extract(tar_info, tmp_dir)
                tmp_path = os.path.join(tmp_dir, tar_info.name)
    shutil.move(tmp_path, city_db)
    os.remove(local_file)

    if os.path.exists(city_db):
        print(
            'The GeoLite2-City DB successfully downloaded and now you '
            'have access to detailed geolocation information of the proxy.'
        )
    else:
        print('Something went wrong, please try again later.')

class WebRequest(object):
    def __init__(self, *args, **kwargs):
        pass

    @property
    def user_agent(self):
        """
        return an User-Agent at random
        :return:
        """
        ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        ]
        return random.choice(ua_list)

    @property
    def header(self):
        """
        basic header
        :return:
        """
        return {'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Accept-Language': 'zh-CN,zh;q=0.8'}

    def get(self, url, header=None, retry_time=2, timeout=10,
            retry_flag=list(), retry_interval=5, *args, **kwargs):
        """
        get method
        :param url: target url
        :param header: headers
        :param retry_time: retry time when network error
        :param timeout: network timeout
        :param retry_flag: if retry_flag in content. do retry
        :param retry_interval: retry interval(second)
        :param args:
        :param kwargs:
        :return:
        """
        headers = self.header
        if header and isinstance(header, dict):
            headers.update(header)
        while True:
            try:
                html = requests.get(url, headers=headers, timeout=timeout, **kwargs)
                if any(f in html.content for f in retry_flag):
                    raise Exception
                return html
            except Exception as e:
                print(e)
                retry_time -= 1
                if retry_time <= 0:
                    # 多次请求失败
                    resp = Response()
                    resp.status_code = 200
                    return resp
                time.sleep(retry_interval)


def getHtmlTree(url, **kwargs):
    """
    获取html树
    :param url:
    :param kwargs:
    :return:
    """

    header = {'Connection': 'keep-alive',
              'Cache-Control': 'max-age=0',
              'Upgrade-Insecure-Requests': '1',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'Accept-Encoding': 'gzip, deflate, sdch',
              'Accept-Language': 'zh-CN,zh;q=0.8',
              }
    # TODO 取代理服务器用代理服务器访问
    wr = WebRequest()
    html = wr.get(url=url, header=header).content
    return etree.HTML(html)


def update_geoip_db():
    print('The update in progress, please waite for a while...')
    filename = 'GeoLite2-City.tar.gz'
    local_file = os.path.join(DATA_DIR, filename)
    city_db = os.path.join(DATA_DIR, 'GeoLite2-City.mmdb')
    url = 'http://geolite.maxmind.com/download/geoip/database/%s' % filename

    urllib.request.urlretrieve(url, local_file)

    tmp_dir = tempfile.gettempdir()
    with tarfile.open(name=local_file, mode='r:gz') as tf:
        for tar_info in tf.getmembers():
            if tar_info.name.endswith('.mmdb'):
                tf.extract(tar_info, tmp_dir)
                tmp_path = os.path.join(tmp_dir, tar_info.name)
    shutil.move(tmp_path, city_db)
    os.remove(local_file)

    if os.path.exists(city_db):
        print(
            'The GeoLite2-City DB successfully downloaded and now you '
            'have access to detailed geolocation information of the proxy.'
        )
    else:
        print('Something went wrong, please try again later.')


class ProxyProvider(object):
    def __init__(self, url_list = [], pattern=None, proxies = [], is_blocked = False):
        self.is_blocked = is_blocked
        # 查找模式
        self.re_ip_port_pattern = re.compile( pattern, re.I )
        # 结果数组
        self.result = []

        if type(url_list) is not list:
            url_list = [ url_list ]
        self.url_list = url_list

        # 需要代理才能访问的
        if self.is_blocked and len(proxies) < 1:
            logger.error("[-] Proxies needed")
            raise Exception("Proxies needed")
        self.proxies = proxies
        self.cur_proxy = self.proxies.pop(0)
        self.lock = None

    def setLock(self, lock):
        self.lock = lock

    def set_logger_prefix(self, prefix):
        self.log_prefix = prefix
        self.logger = logging.getLogger(self.log_prefix)

    @property
    def is_blocked(self):
        return False

    #@retrying.retry(stop_max_attempt_number=3)
    def extract_proxy(self):
        request = WebRequest()
        for url in self.url_list:
            # 必须sleep 不然第二条请求不到数据
            sleep(1)
            response = request.get(url, timeout=5)
            re_ip_port_result = self.re_ip_port_pattern.findall(response.text)

            # 成功捕获, 添加到结果队列中
            if re_ip_port_result:
                self.result.extend([{'host': host, 'port': int(port), 'from': url} for host, port in re_ip_port_result])


class dom_is_rewritten(object):
    """An expectation for checking that an element has a particular css class.
    locator - used to find the element
    returns the WebElement once it has the particular css class
    """
    def __init__(self, pattern):
        self.pattern = pattern
        pass

    def __call__(self, driver):
        html = driver.page_source
        proxy_list = re.findall(self.pattern, html)
        if len(proxy_list): return True
        else: return False

def set_firefoxprofile(proxy_ip, proxy_port):
        """method to update the given preferences in Firefox profile"""
        ff_profile = webdriver.FirefoxProfile()
        #profile = webdriver.FirefoxProfile()
        #profile.accept_untrusted_certs = True
        #profile.DEFAULT_PREFERENCES['frozen']['marionette.contentListener'] = True
        #profile.DEFAULT_PREFERENCES['frozen']['network.stricttransportsecurity.preloadlist'] = False
        #profile.DEFAULT_PREFERENCES['frozen']['security.cert_pinning.enforcement_level'] = 0
        #profile.set_preference('webdriver_assume_untrusted_issuer', False)
        #profile.set_preference("browser.download.folderList", 2)
        #profile.set_preference("browser.download.manager.showWhenStarting", False)
        #profile.set_preference("browser.download.dir", temp_folder)
        #profile.set_preference("browser.helperApps.neverAsk.saveToDisk","text/plain, image/png")
        ## automatic download
        ## 2 indicates a custom (see: browser.download.dir) folder.
        #profile.set_preference("browser.download.folderList", 2)
        ## whether or not to show the Downloads window when a download begins.
        #profile.set_preference("browser.download.manager.showWhenStarting", False)
        #profile.set_preference("browser.download.dir", tempDir)
        #profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
        #                    "application/octet-stream"+
        #                    ",application/zip"+
        #                    ",application/x-rar-compressed"+
        #                    ",application/x-gzip"+
        #                    ",application/msword")
        #
        #fp.set_preference("general.useragent.override","'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'")
        if proxy_ip is not None and proxy_port is not None:
            proxy_port = int(proxy_port)
            ff_profile.set_preference("network.proxy.type", 1)
            ff_profile.set_preference("network.proxy.http", proxy_ip)
            ff_profile.set_preference("network.proxy.http_port", proxy_port)
            ff_profile.set_preference("network.proxy.ssl", proxy_ip)
            ff_profile.set_preference("network.proxy.ssl_port", proxy_port)
            ff_profile.set_preference("network.proxy.ftp", proxy_ip)
            ff_profile.set_preference("network.proxy.ftp_port", proxy_port)

            ff_profile.set_preference("plugin.state.flash", 0)
            ff_profile.set_preference("plugin.state.java", 0)
            ff_profile.set_preference("media.autoplay.enabled", False)
            # 2=dont_show, 1=normal
            ff_profile.set_preference("permissions.default.image", 2)
            ff_profile.set_preference("webdriver.load.strategy", "unstable")

            ff_profile.update_preferences()
        else:
            ff_profile = None
        return ff_profile

    # private methods

class ProxyWithWebdriver(object):
    def __init__(self, url,  **kwargs):
        self.url     = url
        self.pattern = kwargs['pattern'] if kwargs.get('pattern') is not None else None
        self.multi_page = kwargs['multi_page'] if kwargs.get('multi_page') is not None else False
        self.iframe = kwargs['iframe'] if kwargs.get('iframe') is not None else None
        self.driver = None
        self.time_load_page = kwargs['time_load_page'] if kwargs.get('time_load_page') is not None else 30
        self.mode = kwargs['mode'] if kwargs.get('mode') is not None else 'multipages'
        if self.mode == 'multilink':
            self.linktext = kwargs['linktext'] if kwargs.get('linktext') is not None else  None
        self.from_ = kwargs['from_'] if kwargs.get('from_') is not None else None

        self.max_pagenum = kwargs['max_pagenum']if kwargs.get('max_pagenum') is not None  else 10
        self.proxy = kwargs['proxy'] if kwargs.get('proxy') is not None else None
        self.auto_proxy = kwargs['auto_proxy'] if kwargs.get('auto_proxy') is not None else True

        self.logger = logging.getLogger(__name__)

        self.result  = []
        self.lock = None

    def setLock(self, lock):
        self.lock = lock

    def set_logger_prefix(self, prefix):
        self.log_prefix = prefix
        self.logger = logging.getLogger(self.log_prefix)

    def base_url(self, url):

        o = urlparse(url)
        netloc = o.scheme +"://" + o.netloc

        return netloc

    def parse_ip_port(self, url, text):
        re_ip_port_encode_result = None

        if self.pattern is None:
            re_ip_port_encode_result  = re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\d{1,5})", text, re.M)
            re_ip_port_encode_result += re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})", text, re.M)
        else:
            re_ip_port_encode_result  = re.findall(self.pattern, text, re.M)

        netloc = self.base_url(url)
        # 适用于web http 代理的情况下
        if self.from_ : netloc = self.from_

        return [{'host': ip, 'port': int(port) , 'from': netloc } for ip, port in re_ip_port_encode_result]

    def driver_setup(self, url):
        ##为了隐藏浏览器
        #self.display = Display(visible=0, size=(800, 600))
        #self.display.start()

        #caps = DesiredCapabilities.FIREFOX.copy()
        #caps['acceptInsecureCerts'] = True

        options = webdriver.FirefoxOptions()
        options.add_argument('--ignore-certificate-errors')
        #options.add_argument('--height 30')
        #options.add_argument('--width  30')
        options.add_argument('--safe-mode')
        ##设置代理服务器
        #options.set_preference('network.proxy.type', 1)
        #options.set_preference('network.proxy.http',IP)#IP为你的代理服务器地址:如‘127.0.0.0’，字符串类型
        #options.set_preference('network.proxy.http_port', PORT)  #PORT为代理服务器端口号:如，9999，整数类型
        #options.set_preference('permissions.default.image',2)#禁止加载图片
        #options.add_argument('--headless') # 不打开GUI窗口
        #options.add_argument('--browser')
        #options.add_argument('--private')
        #options.add_argument('-url "https://free-ss.site/"')
        #options.add_argument('-P "Profile0"') # -profile "profile_path"
        # capabilities=caps, firefox_profile=profile,

        profile = None

        # 自动检测是否启用代理服务器
        if self.auto_proxy:
            #print("===========")
            # 先测试是否可以直连, 否则使用内置的shadowsocks代理
            need_proxy = False
            try:
                r = requests.get(url, timeout=30, verify=False)
                if r.status_code != 200: need_proxy = True
            except:
                need_proxy = True

            # 如果需要代理服务器
            if need_proxy:
                # 如果, 主动设置代理地址
                if self.proxy:
                    ip, port = self.proxy.split(":")
                else:
                    ip = "127.0.0.1"
                    port = 1082

                profile=set_firefoxprofile(ip, port)

        self.driver = webdriver.Firefox(firefox_options=options, firefox_profile=profile)
        self.driver.set_page_load_timeout(60)

    def driver_get(self, url):
        # html = driver.execute_script("return document.documentElement.outerHTML")
        try:
            #self.driver.set_window_size(100,80)
            #self.driver.set_window_position(-200,-200)
            self.driver.get(url )
            #self.driver.set_window_size(100,80)
            #self.driver.set_window_position(-200,-200)
            #self.driver.minimize_window()
            # WebDriverWait(driver, timeout=30).until(dom_is_rewritten(pattern))
            #
            # b.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.time_load_page)
        except Exception as e:
            self.logger.info("[-] get() error: %s" % ( str(e)))
            pass

    def switch_to_iframe(self, iframe):
        try:
            self.driver.switch_to_frame(iframe)
        except Exception as e:
            self.logger.info("[-] switch_to_iframe() error: %s" % ( str(e)))
            pass

    def driver_cleanup(self):
        try:
            self.driver.delete_all_cookies()
            self.driver.close()
            self.driver = None
        except Exception as e:
            self.logger.info("[-] driver_cleanup() error: %s" % ( str(e)))

    def driver_copy(self, url):
        count = 2
        while count:
            try:
                # 切换到iframe
                if self.iframe : self.switch_to_iframe(self.iframe)

                time.sleep(5)

                #print("before .....")
                # 拷贝文档
                action_chains = ActionChains(self.driver)
                self.driver.find_element_by_xpath('//body').click()
                #Ctrl-a
                action_chains.key_down(Keys.LEFT_CONTROL).send_keys("a").key_up(Keys.LEFT_CONTROL).perform()
                action_chains.reset_actions()
                action_chains = None
                #print("ctrl+a .....")
                time.sleep(2)

                if self.lock: 
                    self.lock.acquire()
                    #print("Locking......")
                text = ""
                try:
                    #Ctrl-c
                    action_chains = ActionChains(self.driver)
                    action_chains.key_down(Keys.LEFT_CONTROL).send_keys("c").key_up(Keys.LEFT_CONTROL).perform()
                    action_chains.reset_actions()
                    action_chains = None
                    time.sleep(2)
                    #print("ctrl+c .....")

                    text = pyperclip.paste()

                finally:
                    #print("UnLocked......")
                    if self.lock: self.lock.release()

                #print(text)
                re_ip_port_result = self.parse_ip_port(url, text)
                #print(re_ip_port_result)

                if len(re_ip_port_result):
                    # 成功获取
                    self.result.extend(re_ip_port_result)
                    return True
                else:
                    # 刷新一下
                    #self.driver.refresh()
                    pass

            except Exception as e:
                self.logger.info("[-] copy() error: %s" % ( str(e)))
                pass

            # 再尝试一次
            count -= 1

        return False

    def next_page(self, pagenum):
        try:
            # 下一页
            #<a href="?stype=1&amp;page=2">2</a>
            #driver.find_element_by_xpath('//li/a[contain(@href, "/en/proxy-list/?start=")]'+str(pagenum+1) +'"]/a').click()
            self.driver.find_element_by_link_text(str(pagenum+1)).click()
            # 页数增加
            return pagenum+1
        except Exception as e:
            self.logger.info("[-] next_page() error: %s" % ( str(e)))
            return None

    def move_mouse_then_click(self):
        pass
        
    def extract_proxy_multipages(self,url) :
        # 1) 初始化driver
        # 2) 打开其实url
        # 3) 获取内容, 并分析其中的ip:port
        # 4) 对于分页的, 进入下一页
        self.driver_setup(url)
        self.driver_get(url)

        pagenum = 1
        while pagenum < self.max_pagenum:
            
            self.move_mouse_then_click()

            #拷贝网页的内容, 并分析其中的IP:PORT
            self.driver_copy(url)

            # 没有分页, 直接退出
            if self.multi_page is False:
                break
            else:
                pagenum = self.next_page(pagenum)
                if pagenum is None: break

        # 清理
        self.driver_cleanup()

    def extract_proxy_multilinks(self,url) :
        # 1) 初始化driver
        # 2) 打开其实url
        # 3) 获取内容, 并分析其中的ip:port
        # 4) 对于分页的, 进入下一页
        self.driver_setup(url)
        self.driver_get(url)

        nextpage = 0
        while nextpage is not None:
            self.move_mouse_then_click()
            nextpage = self.visit_link(self.driver, url, nextpage)
        # 清理
        self.driver_cleanup()

    def all_links(self, driver):
        count = 10
        link_list = driver.find_elements_by_partial_link_text(self.linktext)
        while not link_list:
            count -=1
            if count == 0 : return # 退出吧
            driver.refresh()
            time.sleep(5)
            link_list = driver.find_elements_by_partial_link_text(self.linktext)
        return link_list

    def visit_link(self, driver, url, cur_page_num ):
        try:
            re_ip_port_result = []


            # 获取所有的连接
            link_list = self.all_links(driver)

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
        except Exception as e:
            self.logger.info("[-] visit_link() error: %s" % ( str(e)))
            pass

    def start(self):
        urls = self.url if type(self.url) is list else [ self.url ]

        # 依次处理每个URL
        for i in range(0, len(urls)):
            try:
                if self.mode == 'multipages':
                    self.extract_proxy_multipages(urls[i])
                elif self.mode == 'multilink':
                    self.extract_proxy_multilinks(urls[i])
                else:
                    self.extract_proxy_multipages(urls[i])
                # 暂停一下
                if (i+1) < len(urls): time.sleep(30)
            except Exception as e:
                self.logger.info("[-] Start() error: %s" % ( str(e)))
                return



