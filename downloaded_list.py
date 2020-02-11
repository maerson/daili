#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division, print_function, absolute_import

import gevent.monkey
gevent.monkey.patch_all()

import os
import sys
import json
import time
from datetime import datetime
import copy
import signal
import logging
import math
import re
import random
import requests
import gevent.pool
import geoip2.database
import click
from importlib import import_module
from lxml import etree
from requests.models import Response
from time import sleep
import urllib.request
from importlib import import_module
from collections import OrderedDict
import json
import glob

def wiktionary2019_word_list():
    wfd = open("d:\\wiki_word_list.txt", "w", -1, "utf-8")
    
    for f in glob.glob("D:\\wiktionary2019\\*.csv"):
        fd = open(f, "r", -1, "utf-8")
        for line in fd:
            m = re.search("^(.+)[|]{3}", line)
            wfd.write(m.group(1).strip()+"\n")
            
    wfd.close() 

#    
def get_enwiktionary_all_titles(filename):
    fd_word_list    = open(filename, 'r', -1, encoding="utf_8_sig")
    word_list = {}
    for line in fd_word_list:
        word = line.strip()
        word = word.replace(" ","_")
        word = word.lower()
        word_list[word] = word
    fd_word_list.close()
    return word_list
        
        
def dict_diff(first, second):
    """ Return a dict of keys that differ with another config object.  If a value is
        not found in one fo the configs, it will be represented by KEYNOTFOUND.
        @param first:   Fist dictionary to diff.
        @param second:  Second dicationary to diff.
        @return diff:   Dict of Key => (first.val, second.val)
    """
    diff_1 = {}
    diff_2 = {}
    # Check all keys in first dict
    for key in first.keys():
        if second.get(key) is None:
            diff_1[key] = key
    # Check all keys in second dict to find missing
    for key in second.keys():
        if first.get(key) is None:
            diff_2[key] = key
    return [ diff_1, diff_2]
    
def compare_word_list():
    word_list_json  = get_enwiktionary_all_titles("d:\\enwiktionary-latest-all-titles-in-ns0-filted.txt" )
    word_list_excel = get_enwiktionary_all_titles("d:\\wiki_word_list.txt" )
    
    diff_excel_miss, diff_json_miss = dict_diff(word_list_json, word_list_excel)
    
    letters = {}
    print("json missing....")
    for key in diff_json_miss.keys():
        #for c in key:
        #    letters[c] = c
        if re.search("[¢£ß-ɲα-ừ]", key) is None and re.search("[.]$", key) is None :
            print(key)
    print("========================")
    
    #for key in letters.keys():
    #    print(key)
    
    #print("excel missing....")
    #for key in diff_excel_miss.keys():
    #    print(key)
    #print("========================")
    
def downloaded_list():
    downloaded_file = "d:\\enwiktionary_downloaded_2.txt"
    f = open(downloaded_file, 'w', -1, encoding="utf_8_sig")
    for fpath in glob.glob("d:\\enwiktionary20200106-part2\\*\\*.json"):
        m = re.search("([^\\\\]+)[.]json", fpath)
        fn = m.group(1)
        fn=fn.strip()
        f.write(fn+"\n")
        
    #for fpath in glob.glob("d:\\enwiktionary-en\\*\\*.json"):
    #    m = re.search("([^\\\\]+)[.]json", fpath)
    #    fn = m.group(1)
    #    fn=fn.strip()
    #    f.write(fn+"\n")
        
    f.close()

def downloaded_list_wordnik():
    downloaded_file = "d:\\enwiktionary\\downloaded.txt"
    f = open(downloaded_file, 'w', -1, encoding="utf_8_sig")
    for fpath in glob.glob("d:\\enwiktionary\\*\\*.html"):
        m = re.search("([^\\\\]+)[.]html", fpath)
        fn = m.group(1)
        fn=fn.strip()
        f.write(fn+"\n")
        
        
    f.close()
    
downloaded_list_wordnik()
#compare_word_list()
    
    
    
    

