#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function, absolute_import

import gevent.monkey
import gevent.pool
gevent.monkey.patch_all()

from collections import OrderedDict
from datetime import datetime
from importlib import import_module
from requests.models import Response
import click
import copy
import glob
import html2text
import itertools
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
#import urllib.request

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 3

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def download_index():
    url = 'https://www.dictionary.com/list/'
    for c in [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0']:
        cur_url_base = url + c
        cur_num = 1
        total = 1
        while cur_num <= total:
            cur_url = cur_url_base + "/" + str(cur_num)
            html = None
            try:
                r = requests.get( cur_url, timeout=20, verify=False)
                if r.status_code is not 200:
                    print("failed("+ str(total)+ "):\t" + cur_url )
                    continue
                html = r.content
            
            except Exception:
                print("failed("+ str(total)+ "):\t" + cur_url )
                continue

            html = html.decode("utf-8")            
            # 获取总的页数
            # <a data-page="53" href="/list/a/53">&gt;&gt;</a>
            if cur_num ==1:
                m = re.search('data-page="(?P<page_num>[0-9]+)"[^>]+>&gt;&gt;',html)
                total = int(m.group("page_num"))

            # 保存页面
            fw = open("d:\\dictionary.com\\"+c+"_"+str(cur_num)+".html", 'w', -1, encoding="utf_8_sig")
            fw.write(html)
            fw.close()
            
            cur_num += 1
            
download_index()            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        