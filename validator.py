#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function, absolute_import

import gevent.monkey
gevent.monkey.patch_all()
import gevent.pool

from collections import OrderedDict
from datetime import datetime
import click
import geoip2.database
import glob
import json
import logging
import math
import os
import random
import re
import requests
import signal
import sys
import time
import win32api

if __name__ == '__main__':
    sys.path.append(os.path.dirname(sys.path[0]))
    sys.path.append(os.path.dirname(sys.path[0])+"/plugin")


from utils import signal_name, load_object

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ValidatorByHttpbin:
    base_dir = os.path.dirname(os.path.realpath(__file__))
    def __init__(self, input_proxies_file, output_proxies_file, process_seq=0, process_count=1):
        
        self.input_proxies_file = input_proxies_file
        self.outfile = output_proxies_file+"_"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".txt"
        
        # 多进程模式
        self.process_seq   = process_seq
        self.process_count = process_count
        
        self.post_init()

    def load_proxies_from(self, input_proxies_file):
        logger.info("[*] Load input proxies %s" % ( str(input_proxies_file)))
        input_proxies = []
        proxies_hash = {}

        files = input_proxies_file
        if type(input_proxies_file) is not list: files = [ input_proxies_file ]
        for filepath in files:
            if filepath and os.path.exists(filepath):
                with open(filepath) as fd:
                    for line in fd:
                        try:
                            # 注释行
                            if re.match("^\s*#", line):
                                continue
                            # 如果行是ip:port的样式
                            elif re.match("^\s*[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+\s*[:]\s*[0-9]+\s*$", line):
                                ip, port  =  line.strip().split(":")
                                line = '{ "host": "'+ip+'" , "port": '+str(port.strip().replace('\n','')) +', "from":"unkown"  }'

                            # 以json格式存储
                            line=line.replace("'",'"')
                            # 解析json数据
                            j = json.loads(line)
                            # 去重
                            host = j['host']
                            port = j['port']
                            proxy_hash = '%s:%s' % (host, port)
                            if proxy_hash in proxies_hash:
                                continue
                            proxies_hash[proxy_hash] = True

                            # 添加到队列中
                            input_proxies.append(j)
                        except Exception as e:
                            logger.info("[-] %s : error: %s" % (line, str(e)))
                            #continue
        # 返回需要验证的代理列表
        return input_proxies

    if True:
        # 验证的函数, 通过httpbin.org来验证
        def _validate_one_proxy(self, proxy, scheme='http'):
            try:
                country = proxy.get('country')
                host = proxy.get('host')
                port = proxy.get('port')
                scheme_input = scheme

                request_proxies= { scheme: "%s:%s" % (host, port) }
                if scheme == 'sock4' or scheme == 'sock5':
                    request_proxies = { 'http': "http://%s:%s" % (host, port), 'https': "https://%s:%s" % (host, port) }
                    scheme = 'http'

                request_begin = time.time()
                try:
                    response_json = requests.get(
                        "%s://httpbin.org/get?show_env=1&cur=%s" % (scheme, request_begin),
                        proxies=request_proxies,
                        timeout=5
                    ).json()
                except:
                    return None

                request_end = time.time()

                if str(request_begin) != response_json.get('args', {}).get('cur', ''):
                    return None

                # 代理的匿名性, 国家信息, export??, 反应时间
                anonymity = self._check_proxy_anonymity(response_json)
                country = country or self.geoip_reader.country(host).country.iso_code
                export_address = self._check_export_address(response_json)

                # 返回结果
                return {
                    "type": scheme_input,
                    "host": host,
                    "port": port,
                    "from": proxy.get('from')
                }
            except :
                return None


        def _check_proxy_anonymity(self, response):
            via = response.get('headers', {}).get('Via', '')

            if self.origin_ip in json.dumps(response):
                return 'transparent'
            elif via and via != "1.1 vegur":
                return 'anonymous'
            else:
                return 'high_anonymous'

        def _check_export_address(self, response):
            origin = response.get('origin', '').split(', ')
            if self.origin_ip in origin:
                origin.remove(self.origin_ip)
            return origin
            
        def post_init(self):
            self.origin_ip = None
            self.geoip_reader = None
    
            rp = requests.get('http://httpbin.org/get')
            self.origin_ip = rp.json().get('origin', '')
            logger.info("[*] Current Ip Address: %s" % self.origin_ip)
    
            self.geoip_reader = geoip2.database.Reader(os.path.join(self.base_dir, 'data/GeoLite2-Country.mmdb'))        

    if "验证预设的代理列表, 通常是历史数据":
        def validate_input_proxies(self):
            input_proxies = self.load_proxies_from(self.input_proxies_file)

            logger.info("[*] Validate input proxies")
            self._validate_proxy_list(input_proxies)


        def _validate_proxy_list(self, proxies, timeout=90):
            valid_proxies = []

            def save_result(p):
                if p and len(str(p)):
                    valid_proxies.append(p)

            # 在多进程下面, 只检测部分
            if self.process_count > 1:
                num_per_part = int((len(proxies)+self.process_count-1)/self.process_count)
                start = self.process_seq*num_per_part
                end   = (self.process_seq+1)*num_per_part
                proxies = proxies[start:end]

            # 每100 检查一次
            total_num = len(proxies)
            step = 500
            pool = gevent.pool.Pool(500)
            for i in range(0, total_num, step):
                group = proxies[i:i+step]
                for proxy in group:
                    pool.apply_async(self._validate_one_proxy, args=(proxy, 'http'), callback=save_result)
                    pool.apply_async(self._validate_one_proxy, args=(proxy, 'https'), callback=save_result)
                    pool.apply_async(self._validate_one_proxy, args=(proxy, 'socks4'), callback=save_result)
                    pool.apply_async(self._validate_one_proxy, args=(proxy, 'socks5'), callback=save_result)

                is_empty = pool.join(timeout=timeout)
                if not is_empty :
                    # 还没有检查完整
                    print("**** validation is not done!")

                pool.kill()

                # 即时保存检验过的traffic
                self.save_proxies(valid_proxies)
                valid_proxies = []
                print("progress: {}/{}".format(i, total_num))
                time.sleep(1)

            return valid_proxies

    def save_proxies(self, valid_proxies):
    
        # 多进程下, 需要加锁
        #if self.process_count > 1:
            
        outfile = open(self.outfile, 'a', -1, "utf-8")
        for item in valid_proxies:
            try:
                outfile.write("%s\n" % json.dumps(item))
            except:
                #self.outfile.write("%s\n" % str(item))
                pass
        outfile.close()


class ValidatorByWiktonary(ValidatorByHttpbin):

    def _validate_one_proxy(self, proxy, scheme='http'):
        try:
            host = proxy.get('host')
            port = proxy.get('port')

            scheme_input = scheme

            # 测试sock4/5, http(s)
            request_proxies = { scheme: "%s:%s" % (host, port) }
            if scheme == 'socks4' or scheme == 'socks5':
                request_proxies = { 'http': "http://%s:%s" % (host, port), 'https': "https://%s:%s" % (host, port) }
                scheme = 'http'

            #url = '%s://en.wiktionary.org/wiki/Aanstrengung'
            urls = ['www.baidu.com',
                    'www.bing.com'
                   ]
            url = '%s://' + random.choice(urls)
            r = requests.get( url % (scheme), proxies=request_proxies, timeout=20, verify=False)

            # 5xx Server errors
            if r.status_code != 200: return None

            # 返回结果
            return {
                "type": scheme_input,
                "host": host,
                "port": port,
                "from": proxy.get('from')
                }
        except Exception as e:
            pass
        return None

@click.command()
@click.argument('process_seq')
def main(process_seq):
    time.sleep(int(process_seq)*30)
    
    process_count = 6
    
    fs = []
    fs += glob.glob("valid_proxies*.txt")
    fs += glob.glob("web_proxies*.txt")
    #fs += glob.glob("web_proxies_2019-12-25*.txt")
    print(fs)

    #v = ValidatorByHttpbin( 'web_proxies_2019-12-25-20-53-13.txt' , "valid_proxies")
    #v.validate_input_proxies()

    v = ValidatorByWiktonary(fs, "x_valid_proxies", int(process_seq), process_count)
    v.validate_input_proxies()    
    

if __name__ == '__main__':
    main()  

