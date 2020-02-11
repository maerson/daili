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
import shutil
from lxml import etree
import bs4
from bs4 import BeautifulSoup
import html2text



def visit_object(path_info, obj, path):
    t = type(obj)
    if t == list:
        for i in range(0,len(obj)):
            item = obj[i]
            visit_object(path_info, item, path+"[].")
    elif t == dict:
        for k, v in obj.items():
            visit_object(path_info, v, path+"."+k+".")
    else:
        # 最终的地方
        #print(path)
        path_info[path] = path


# 遍历所有的json文件, 分析其中的路径信息
def downloaded_list():
    path_info = {}
    count = 0
    total_count = 1
    f_pathInfo = open("path_info.txt", 'a', -1, encoding="utf_8_sig")
    for fpath in glob.glob("d:\\enwiktionary\\*\\*.json"):
        #m = re.search("([^\\\\]+)[.]json", fpath)
        #fn = m.group(1)
        #fn=fn.strip()
        #f.write(fn+"\n")
        #print("==== " + fpath)
        try:
            fj = open(fpath, 'r', -1, encoding="utf_8_sig")
            data = fj.read()
            fj.close()
            j = json.loads(data)
            visit_object(path_info, j,"")

            data= None
            j = None
        except:
            print(fpath)

        count += 1
        if count > 3000:
            print("total: "+ str(total_count*3000))

            text = "\n".join(path_info.keys())
            f_pathInfo.write(text+"\n")
            text = None

            count = 0
            total_count += 1
            path_info = {}

    #
    f_pathInfo.close()


# .en.[]..definitions.[]..definition.
# .en.[]..definitions.[]..examples.[].
# .en.[]..definitions.[]..parsedExamples.[]..example.
# .en.[]..definitions.[]..parsedExamples.[]..footer.
# .en.[]..definitions.[]..parsedExamples.[]..translation.
# .en.[]..language.
# .en.[]..partOfSpeech.
# .other.[]..definitions.[]..definition.
# .other.[]..definitions.[]..examples.[].
# .other.[]..definitions.[]..parsedExamples.[]..example.
# .other.[]..definitions.[]..parsedExamples.[]..literally.
# .other.[]..definitions.[]..parsedExamples.[]..source.
# .other.[]..definitions.[]..parsedExamples.[]..translation.
# .other.[]..definitions.[]..parsedExamples.[]..transliteration.
# .other.[]..language.
# .other.[]..partOfSpeech.
#

# .API..response..operation..name.
# .API..response..operation..result..message.
# .API..response..operation..result..status.
# .API..response..operation..result..statuscode.
# .API..version.
#
# 还存在一些这样的样式
#"language": "Chinese Pidgin English",
#"language": "Middle English",
#"language": "Old English",

def filter_english_words():
    english_word_count = 96*10000
    word_count_1 = 0
    word_count_2 = 0
    word_count_3 = 0
    for fpath in glob.glob("d:\\enwiktionary20200106\\*\\*.json"):
        try:
            fj = open(fpath, 'r', -1, encoding="utf_8_sig")
            data = fj.read()
            fj.close()
            j = json.loads(data)
            if j.get('en'):
                dst_dir = "d:\\enwiktionary-en\\en-"+"{0:03d}".format(int(english_word_count/10000))
                if english_word_count%10000 == 0 :
                    # 创建新的目的目录
                    os.mkdir(dst_dir)
                    #time.sleep(1)
                # 移动文件
                shutil.move(fpath, dst_dir)
                english_word_count += 1
            else:
                err_ = [
                    'responseCode',
                    'err',
                    'errmsg',
                    'error',
                    'errorType',
                    'handle',
                    'message',
                    'msg',
                    'rtn',
                    'server',
                    'status',
                    'success'
                ]

                other_ = 'other'
                api_   = 'API'

                dst_dir = None

                if j.get(other_):
                    dst_dir = "d:\\enwiktionary-en\\other-"+"{0:03d}".format(int(word_count_1/10000))
                    if word_count_1%10000 == 0 :
                        # 创建新的目的目录
                        os.mkdir(dst_dir)
                    word_count_1 +=1
                    shutil.move(fpath, dst_dir)
                elif j.get(api_):
                    dst_dir = "d:\\enwiktionary-en\\api-"+"{0:03d}".format(int(word_count_2/10000))
                    if word_count_2%10000 == 0 :
                        # 创建新的目的目录
                        os.mkdir(dst_dir)
                    word_count_2 +=1
                    shutil.move(fpath, dst_dir)
                else:
                    for attr in err_:
                        if j.get(attr):
                            dst_dir = "d:\\enwiktionary-en\\err-"+"{0:03d}".format(int(word_count_3/10000))
                            if word_count_3%10000 == 0 :
                                # 创建新的目的目录
                                os.mkdir(dst_dir)
                            word_count_3 +=1
                            shutil.move(fpath, dst_dir)
                            break


            data= None
            j = None
        except:
            print(fpath)

def to_csv():
    word_list = {}
    f_dup = open("d:\\enwiktionary_en_20200106.dup.txt", 'w', -1, encoding="utf_8_sig")
    f_out = open("d:\\enwiktionary_en_20200106.csv", 'w', -1, encoding="utf_8_sig")
    for fpath in glob.glob("d:\\enwiktionary-en\\*\\*.json"):
        try:
            fj = open(fpath, 'r', -1, encoding="utf_8_sig")
            data = fj.read()
            fj.close()
            j = json.loads(data)
            def_en = j.get('en')

            m = re.search("([^\\\\]+)[.]json", fpath)
            word = m.group(1).strip()

            old_path = word_list.get(word)
            if old_path:
                #print("*** "+ fpath)
                f_dup.write("-- "+old_path+"\n")
                f_dup.write("++ "+fpath+"\n")
                continue
            else:
                word_list[word] = fpath

            if def_en:
                if type(def_en) is not list:
                    def_en = [ def_en ]
                for d in def_en:
                    lang = d.get('language')
                    pos  = d.get('partOfSpeech')
                    def_list = d.get('definitions')
                    if type(def_list) is not list:
                        def_list = [ def_list ]
                    for dd in def_list:
                        d_c = dd.get("definition")
                        examples = dd.get("examples") # 多个例子

                        d_c = d_c.replace('\\"', '"').replace("\r\n","").replace("\n","")
                        f_out.write("{0}|||{1}|||{2}|||{3}\n".format(word, lang, pos, d_c))

            data= None
            j = None
        except Exception as e:
            print(fpath+str(e))

    f_out.close()
    f_dup.close()
#downloaded_list()
#filter_english_words()
#to_csv()


def visit_html_object(f_dump, tag, path):
    for child in tag.children:
        if type(child) is bs4.element.Tag:
            visit_html_object(f_dump, child, path+"."+tag.name)
        else:
            #print("-- "+tag.name + "." + str(child))
            pass

    for attr in tag.attrs:
        #print(type(attr))
        #print(str(attr))
        #print(str(tag.attrs))
        f_dump.write(path+"."+tag.name + "." + attr + "  "+ str(tag.attrs[attr])+"\n")

def parse_csv():
    f_dump = open("d:\\enwiktionary_en_20200106.csv_dump", 'w', -1, encoding="utf_8_sig")
    f_out = open("d:\\enwiktionary_en_20200106.csv", 'r', -1, encoding="utf_8_sig")
    for line in f_out:
        line = line.strip()
        # 空行
        if len(line)<1: continue

        try:
            m= re.search("^(?P<word>.+)[|]{3}(?P<lang>.+)[|]{3}(?P<pos>.+)[|]{3}(?P<definition>.*)$", line)
            # 分析词的变形

            word = m.group("word")
            word = word.replace("_", " ")
            lang = m.group("lang")
            pos  = m.group("pos")
            html = m.group("definition")
            soup = BeautifulSoup(html, "lxml")
            #f_dump.write(soup.prettify()+"\n")
            visit_html_object(f_dump, soup, "")

            #print(word)
        except Exception as e:
            print(line+str(e))
            return


    f_out.close()
    f_dump.close()



def parse_csv_2():
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    #print(h.handle("<p>Hello, <a href='https://www.google.com/earth/'>world</a>!"))

    f_dump = open("d:\\enwiktionary_en_20200106.csv_form_dump", 'w', -1, encoding="utf_8_sig")
    f_out = open("d:\\enwiktionary_en_20200106.csv_3", 'r', -1, encoding="utf_8_sig")
    for line in f_out:
        line = line.strip()
        # 空行
        if len(line)<1: continue

        try:
            m= re.search("^(?P<word>.+)[|]{3}(?P<lang>.+)[|]{3}(?P<pos>.+)[|]{3}(?P<definition>.*)$", line)
            # 分析词的变形

            word = m.group("word")
            word = word.replace("_", " ")
            lang = m.group("lang")
            pos  = m.group("pos")
            html = m.group("definition")
            #soup = BeautifulSoup(html, "lxml")
            #f_dump.write(soup.prettify()+"\n")
            #visit_html_object(f_dump, soup, "")
            f_dump.write(h.handle(html).replace("\n", "")+"\n")

            # 缩写单词不处理
            # Abbreviation of (fire) extinguisher.
            # Abbreviated form of deceased.
            # Acronym of (an animal of) any solid colour other than black.

            #print(word)
        except Exception as e:
            print(line+str(e))
            return


    f_out.close()
    f_dump.close()

simple_form_pattern = [
            "A deliberately incomplete spelling of",
            "A dialectal or obsolete form of",
            "A diminutive of",
            "African-American Vernacular and Southern US form of",
            "African-American Vernacular form of",
            "Alternate form of",
            "Alternative form of",
            "Alternative letter-case form of",
            "Anglicisation of",
            "Anglicised form of",
            "Apheretic form of",
            "Aphetic form of",
            "Apocopic form of",
            "Appalachia form of",
            "Archaic form of",
            "Attributive form of",
            "British Virgin Islands Abbreviation of",
            "British standard form of",
            "Clipping of",
            "Corruption of",
            "Dated form of",
            "Derivatives of",
            "Dialectal form of",
            "Diminutive of",
            "Eggcorn of",
            "Elongated form of",
            "Emphatic form of",
            "Emphatic synonym of",
            "Equatorial Guinea Abbreviation of",
            "Erroneous, computer-generated form of",
            "Euphemistic form of",
            "Form of",
            "Former name of",
            "Honorific alternative letter-case form of",
            "Informal form of",
            "Less common form of",
            "Lincolnshire spinach Alternative form of",
            "Malapropistic misconstruction of",
            "Misconstruction of",
            "Mistaken form of",
            "Netherlands Abbreviation of",
            "Non-Oxford British English form of",
            "Non-Oxford British English standard form of",
            "Non-standard capitalisation of",
            "Non-standard form of",
            "Nonstandard form of",
            "Obsolete form of",
            "Oxford British English form of",
            "Prevocalic form of",
            "Rare form of",
            "Rhodesia and Zimbabwe form of",
            "Scottish form of",
            "Short for",
            "Syncopic form of",
            "Synonym of",
            "US English form of",
            "US form of",
            "US standard form of",
            "Uncommon form of",
            "Variant form of",
            "Variant of",
            "a synonym of",
            "acronym of",
            "alternate, archaic form of",
            "alternative capitalization of",
            "alternative form of"    ,
            "alternative typography of",
            "animate imperative of",
            "attributive form of",
            "bowdlerization of",
            "censored form of",
            "clipping of",
            "clitic form of",
            "colloquial form of",
            "combining form of",
            "dialectal variant of",
            "emphatic form of",
            "euphemism of",
            "exact synonym of",
            "extended form of",
            "female equivalent of",
            "feminine of",
            "form of",
            "genitive of",
            "gerund of",
            "guardian Initialism of",
            "infinitive of",
            "initialism of",
            "malapropism of",
            "masculine equivalent of ",
            "mild form of",
            "misconstructed plural of",
            "misconstruction of",
            "non-official form of",
            "nonstandard form of",
            "obsolete emphatic of",
            "obsolete or nonstandard form of",
            "obsolete typography of",
            "prerhotic form of",
            "prevocalic form of",
            "prevocalic variant of",
            "rare alternative form of",
            "variant form of",
            "variant of",
            "verbal noun of",
            "Informal spelling of",
            "An emphatic form of",
            ": Synonym of",
            ": Alternative form of",
            "A form of",
            "A transliteration of",
            # or derived from
            # a variant of
            # The ordinal form
            # A derivative of
            # derived from the
            # A dialect of
            # a variety of
            # Junior synonym of
]

important_pattern = [
            "A plural of",
            "Alternative irregular form of the past participle of",
            "Misconstructed plural form of",
            "Obsolete or dialectal plural of",
            "Possessive of",
            "Present participle and gerund of",
            "Strong simple past tense of",
            "The comparative form of",
            "The ordinal numeral form of",
            "Third-person singular simple present indicative form of",
            "a plural of",
            "a scientist, singular of",
            "agent noun of",
            "alternative past of",
            "alternative past participle of",
            "alternative past participle",
            "alternative plural of",
            "alternative simple past of",
            "alternative third-person singular past of",
            "collective plural of",
            "comparative degree of",
            "comparative form of",
            "first-person plural simple past indicative of",
            "first-person plural simple present of",
            "first-person simple past of",
            "first-person singular present indicative of",
            "first-person singular simple past indicative of",
            "first/second/third-person plural simple past indicative of",
            "first/second/third-person singular/plural simple past subjunctive of",
            "first/third-person singular simple past indicative of",
            "inflection of",
            "neuter singular of",
            "obsolete past participle of",
            "obsolete plural of",
            "obsolete simple past of",
            "past participle of",
            "past tense of",
            "plural of"             ,
            "plural simple past of",
            "plural simple present of",
            "possessive case of",
            "possessive form of",
            "present of",
            "present participle of",
            "second-person plural simple present of",
            "second-person singular of",
            "second-person singular present subjunctive of",
            "second-person singular simple past form of",
            "second-person singular simple past indicative of",
            "second-person singular simple past subjunctive of",
            "second-person singular simple present form of",
            "simple past and past participle of",
            "simple past of",
            "simple past plural of",
            "simple past singular of",
            "simple past tense and past participle of" ,
            "simple past tense of",
            "singular of",
            "spurious plural of",
            "superlative degree of",
            "superlative form of",
            "third-person plural present indicative of",
            "third-person plural simple present of",
            "third-person simple past of",
            "third-person singular of",
            "third-person singular present simple form of",
            "third-person singular simple past indicative of",
            "third-person singular simple present indicative of",
            "third-person singular simple present subjunctive of",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
]

spelling_pattern = [
            "Alternative spelling of",
            "American spelling and Oxford British English standard spelling of",
            "American spelling form of",
            "American spelling spelling of",
            "American spelling standard form of",
            "American spelling standard spelling of",
            "An English surname, Alternative spelling of",
            "An English surname​, Alternative spelling of",
            "An Irish surname​, Alternative spelling of",
            "Archaic spelling of",
            "Australia, Canada, Ireland, New Zealand, and Britain standard spelling of",
            "Britain and Australia spelling of",
            "Britain and Canada spelling of",
            "Britain and Canada standard spelling of",
            "Britain and Ireland standard spelling of",
            "Britain spelling of",
            "Britain standard spelling of",
            "Britain, Australia, New Zealand, and Canada spelling of",
            "Britain, Australia, and Canada spelling of",
            "Britain, Australia, and New Zealand standard spelling of",
            "Britain, Canada, Australia, New Zealand, Ireland, and South Africa spelling of",
            "Britain, Canada, Australia, and New Zealand standard spelling of",
            "Britain, Canada, Ireland, South Africa, Australia, and New Zealand spelling of",
            "Britain, Canada, New Zealand, Australia, and Ireland spelling of",
            "Britain, Ireland, Australia, New Zealand, and South Africa spelling of",
            "Britain, Ireland, Canada, Australia, New Zealand, and South Africa spelling of",
            "British spelling and Canada standard spelling of",
            "British spelling and Canadian spelling spelling of",
            "British spelling and Canadian spelling standard spelling of",
            "British spelling form of",
            "British spelling spelling of",
            "British spelling standard form of",
            "British spelling standard spelling of",
            "British spelling, Canadian spelling, Commonwealth of Nations, and Irelandstandard spelling of",
            "British, Australian, New Zealand spelling and Canadian spelling standardspelling of",
            "Canada spelling of",
            "Canada standard spelling of",
            "Canada, US standard spelling of",
            "Canadian spelling of",
            "Commonwealth of Nations spelling of",
            "Commonwealth of Nations standard spelling of",
            "Dated spelling of",
            "Deliberate misspelling of",
            "Etymologically incorrect rare spelling of",
            "Etymologically incorrect spelling of",
            "Euphemistic spelling of",
            "Eye dialect spelling of",
            "Federal Reserve System. Alternative spelling of",
            "Feminist spelling of",
            "Former spelling of",
            "Latinised spelling of",
            "Leet spelling of",
            "Misspelling of",
            "Most common English spelling of",
            "New Zealand spelling of",
            "Non-Oxford British English and New Zealand standard spelling of",
            "Non-Oxford British English spelling of",
            "Non-Oxford British English standard spelling of",
            "Nonstandard spelling of",
            "North American spelling standard spelling of",
            "Obsolete spelling of",
            "Oxford British English spelling of",
            "Partly Latinised spelling of",
            "Phonetic alternative spelling of",
            "Pronunciation spelling of",
            "Rare spelling of",
            "Sixteenth-Century Scottish spelling of",
            "Standard spelling of",
            "US alternative spelling of",
            "US and Oxford British English standard spelling of",
            "US spelling of",
            "US standard spelling of",
            "US, Canada, and Oxford British English standard spelling of",
            "Uncommon spelling of",
            "alternative spelling of",
            "archaic, chiefly Scottish spelling of",
            "chiefly US spelling of",
            "deliberate misspelling of",
            "misspelled form of",
            "nonstandard or archaic spelling of",
            "rare spelling of",
            "",
            "",
            "",
            "",
            "",
            "",
]

short_pattern = [
            "Ellipsis of"   ,
            "Contraction of",
            "Initialism of" ,
            "abbreviation of",
            "contraction of",
            "contracted form of",
            "Postal abbreviation of",
            "shortened form of",
            "Abbreviated form of",
            ": Initialism of",
            ": Abbreviation of",
            "",
]

dummy = [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
]

#parse_csv_2()
def parse_csv_3():
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    #print(h.handle("<p>Hello, <a href='https://www.google.com/earth/'>world</a>!"))

    f_dump = open("d:\\enwiktionary_en_20200106_past_tense.csv", 'w', -1, encoding="utf_8_sig")
    f_out = open("d:\\enwiktionary_en_20200106.csv_3", 'r', -1, encoding="utf_8_sig")
    for line in f_out:
        line = line.strip()
        # 空行
        if len(line)<1: continue

        try:
            m= re.search("^(?P<word>.+)[|]{3}(?P<lang>.+)[|]{3}(?P<pos>.+)[|]{3}(?P<definition>.*)$", line)
            # 分析词的变形

            word = m.group("word")
            word = word.replace("_", " ")
            lang = m.group("lang")
            pos  = m.group("pos")
            html = m.group("definition")

            text = h.handle(html).replace("\n", "")+"\n"

            pattern1 = "^simple past tense and past participle of (?P<form>.+)$"
            pattern2 = "^simple past tense and past participle of (?P<form>[a-zA-Z0-9_' -]+)[.;]?\s*$"
            m = re.search(pattern1, text)
            if m:
                n = re.search(pattern2, text)
                if n:
                    #f_dump.write("*,"+word+","+n.group('form')+"\n")
                    pass
                else:
                    #f_dump.write(":,"+word+","+m.group('form')+"\n")
                    pass
                continue

            pattern1 = "^plural of (?P<form>.+)$"
            pattern2 = "^plural of (?P<form>[a-zA-Z0-9_' -]+)[.;]?\s*$"
            pattern3 = "^plural of (?P<form>[a-zA-Z0-9_' -]+)[.;]?\s*(?P<other>.+?)$"
            m = re.search(pattern1, text)
            if m:
                n = re.search(pattern2, text)
                if n:
                    # 如果有多个单词组成, 可能是不正确的
                    form = n.group('form')
                    real_word_list = form.split(" ")
                    if len(real_word_list) != len(word.split(" ")): # 与单词中词的个数必须相等
                        f_dump.write("*2,"+word+","+form+"\n")
                    else:
                        f_dump.write("*1,"+word+","+form+"\n")
                    pass
                else:
                    k = re.search(pattern3, text)
                    if k:
                        if len(k.group('form').split(" "))  != len(word.split(" ")):
                            f_dump.write("*3,"+word+","+k.group('form')+","+k.group('other')+"\n")
                        else:
                            f_dump.write("*4,"+word+","+k.group('form')+","+k.group('other')+"\n")
                    else:
                        f_dump.write("*5,"+word+","+m.group('form')+"\n")
                    pass
                continue




            # 缩写单词不处理
            # Abbreviation of (fire) extinguisher.
            # Abbreviated form of deceased.
            # Acronym of (an animal of) any solid colour other than black.

            #print(word)
        except Exception as e:
            print(line+str(e))
            return


    f_out.close()
    f_dump.close()



def parse_csv_4():

    #print(h.handle("<p>Hello, <a href='https://www.google.com/earth/'>world</a>!"))

    f_dump = open("d:\\enwiktionary_en_20200106_past_tense.csv", 'w', -1, encoding="utf_8_sig")
    f_out = open("d:\\enwiktionary_en_20200106.csv_3", 'r', -1, encoding="utf_8_sig")

    full_pattern = "==="
    p = simple_form_pattern + important_pattern + spelling_pattern + short_pattern
    for item in p:
        if len(item.strip()) < 1: continue

        item = item.replace("-", "[-]")
        full_pattern += "|" + item

    full_pattern = "("+full_pattern.replace("===|", "")+")"
    #print(full_pattern)


    for line in f_out:
        line = line.strip()
        # 空行
        if len(line)<1: continue

        try:
            m= re.search("^(?P<word>.+)[|]{3}(?P<lang>.+)[|]{3}(?P<pos>.+)[|]{3}(?P<definition>.*)$", line)
            # 分析词的变形

            word = m.group("word")
            word = word.replace("_", " ")
            lang = m.group("lang")
            pos  = m.group("pos")
            html = m.group("definition")
            subword_count = len(word.split(" ")) # 当前复合单词由几个单词组成

            text = h.handle(html).replace("\n", "")

            pattern1 = "^"+full_pattern+"(?P<form>.+)$"
            pattern2 = "^"+full_pattern+"(?P<form>[a-zA-Z0-9_' -]+)\s*[.;]?(?P<more>\s*: (most|most)\s*[a-zA-Z0-9_' -]+)?\s*$"
            pattern3 = "^"+full_pattern+"(?P<form>[a-zA-Z0-9_' -]+)\s*[.;]?\s*(?P<other>.+?)$"
            m = re.search(pattern1, text, re.I)
            if m:
                n = re.search(pattern2, text, re.I)
                if n:
                    # 如果有多个单词组成, 可能是不正确的
                    form = n.group('form').strip()
                    if len(form.split(" ")) == subword_count: # 与单词中词的个数必须相等
                        f_dump.write("*1,"+word+","+form+"\n")
                    else:
                        f_dump.write("*2,"+word+","+form+"\n")
                    pass
                else:
                    k = re.search(pattern3, text, re.I)
                    if k:
                        form = k.group('form').strip()
                        if len(form.split(" "))  != subword_count:
                            f_dump.write("*3,"+word+","+form+","+k.group('other')+"\n")
                        else:
                            f_dump.write("*4,"+word+","+form+","+k.group('other')+"==="+text+"\n")
                    else:
                        f_dump.write("*5,"+word+","+m.group('form')+"\n")
                    pass
                continue
            else:
                f_dump.write("*6,"+text+"\n")
        except Exception as e:
            print(line+str(e))
            return


    f_out.close()
    f_dump.close()

#parse_csv_4()

def parse_csv_5():
    f_dump = open("d:\\enwiktionary_en_20200106.csv_dump_split", 'w', -1, encoding="utf_8_sig")
    f_input = open("d:\\enwiktionary_en_20200106.csv", 'r', -1, encoding="utf_8_sig")
    for line in f_input:
        line = line.strip()
        # 空行
        if len(line)<1: continue

        try:
            m= re.search("^(?P<word>.+)[|]{3}(?P<lang>.+)[|]{3}(?P<pos>.+)[|]{3}(?P<definition>.*)$", line)
            # 分析词的变形

            word = m.group("word")
            word = word.replace("_", " ")
            lang = m.group("lang")
            pos  = m.group("pos")
            html = None
            html = m.group("definition")
            subword_count = len(word.split(" ")) # 当前复合单词由几个单词组成

            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_emphasis = True

            text = h.handle(html).replace("\n", " ")
            #if re.search("participle|past|present|singular|plural|possessive|tense|comparative|superlative", text):
            #    f_dump.write(text+"\n")
            #    continue
            #else:
            #    continue
            text_segs = re.split("[;.:,()]", text)

            word_pattern  = "[a-zA-Z0-9_'&-]+"
            word2_pattern = "^(?P<word2>"+word_pattern+"\s+"+word_pattern+"\s+"+word_pattern+")"
            for seg in text_segs:
                seg = seg.strip().replace("\r\n", " ").replace("\n", " ")
                # 取前两个单词
                m = re.search(word2_pattern, seg)
                if m:
                    f_dump.write("** "+m.group("word2")+"\n")
                else:
                    f_dump.write(seg+"\n")

            #print(word)
        except Exception as e:
            print(line+str(e))
            return


    f_input.close()
    f_dump.close()


pattern = [
"third-person singular simple present subjunctive of",
"third-person singular simple present indicative of",
"third-person singular simple present indicative form of",
"third-person singular simple past indicative of",
"third-person singular present simple form of",
"third-person singular of",
"third-person simple past of",
"third-person plural simple present of",
"third-person plural present indicative of",
"simple past tense of",
"simple past tense and past participle of",
"simple past singular of",
"simple past plural of",
"simple past and past participle of",
"second-person singular simple present of",
"second-person singular simple present form of",
"second-person singular simple past subjunctive of",
"second-person singular simple past indicative of",
"second-person singular simple past form of",
"second-person singular present subjunctive of",
"second-person singular of",
"second-person plural simple present of",
"second-person plural",
"present participle of",
"plural simple past of",
"first-person singular present indicative of",
"first-person simple past of",
"first-person plural simple present of",
"first-person plural simple past indicative of",
"alternative third-person singular past of",
"alternative simple past of",
"alternative plural of",
"alternative past participle of",
"alternative past of",
"Third-person singular simple present indicative form of",
"Present participle and gerund of",
"singular of",
"simple past of",
"plural of",
"plural simple present of",
"past participle of",
"past tense of",
]

whole_pattern = "|".join(p.strip().replace("-", "[-]") for p in pattern)

#print(whole_pattern)



#parse_csv_5()
def parse_csv_6():
    f_dump = open("d:\\enwiktionary_en_20200106_without_form.csv", 'w', -1, encoding="utf_8_sig")
    f_input = open("d:\\enwiktionary_en_20200106.csv", 'r', -1, encoding="utf_8_sig")
    for line in f_input:
        line = line.strip()
        # 空行
        if len(line)<1: continue

        try:
            m= re.search("^(?P<word>.+)[|]{3}(?P<lang>.+)[|]{3}(?P<pos>.+)[|]{3}(?P<definition>.*)$", line)
            # 分析词的变形

            word = m.group("word")
            word = word.replace("_", " ")
            word = word.strip()
            lang = m.group("lang")
            pos  = m.group("pos")
            html = None
            html = m.group("definition")
            subword_count = len(re.split("[ ]",word)) # 当前复合单词由几个单词组成

            # 带大写字母, 数字等, 不关心
            if subword_count > 1 or re.search("^[a-z'_-]+$", word) is None:
                #f_dump.write("*1,"+word+","+form+"\n")
                continue

            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_emphasis = True

            text = h.handle(html).replace("\n", " ").replace("\\-", "-")

            # 比较级/最高级特殊处理
            #wiseliest  wisely  (adverb): most wisely
            #abjectest  abject  : most abject
            #cs_pattern= "(comparative form of|superlative form of)\s*(?P<word2>[a-zA-Z-]+)\s*([(]adverb[)])?:\s*(?P<word3>(more|most)\s+[a-zA-Z-]+)"
            cs_pattern= "(superlative form of)\s*(?P<word2>[a-zA-Z-]+)\s*([(]adverb[)])?:\s*(?P<word3>(more|most)\s+[a-zA-Z-]+)"
            m = re.search("^\s*"+cs_pattern+"(?P<rest>.+)$", text, re.I)
            if m:
                pos = "comparative form"
                if re.search("superlative form of", text, re.I):
                    pos = "superlative form"
                #f_dump.write(word+"|||"+lang+"|||"+pos+"|||"+m.group('word2').strip()+"|||"+m.group('word3').strip()+"|||"+m.group('rest').strip()+"\n")
                continue
            #continue
            #m = re.search("^plural of (?P<form>.+)$", text)
            #whole_pattern= "comparative form of"#"superlative form of"

            m = re.search("^\s*("+whole_pattern+")(?P<form>.+)$", text, re.I)
            if m:
                pos = ""
                for p in pattern:
                    if re.search(p, text, re.I):
                        pos = p
                        break

                form = m.group("form").strip()
                if len(form.split(" ")) == subword_count:
                    #f_dump.write(word+"|||"+lang+"|||"+pos+"|||"+form+"\n")
                    continue

                if re.search("[-]", word) and re.search("[-]", form) is None:
                    # 是复合词, 忽略之
                    continue

                m = re.search("^(?P<word>[a-zA-Z0-9_'-]+)(?P<rest>\s*([(;.,:-]|\s[A-Z]|\sa\s|\san\s|\sthe\s).+)$", form)
                if m:
                    #f_dump.write(word+"|||"+lang+"|||"+pos+"|||"+m.group('word').strip()+"|||"+m.group('rest').strip()+"\n")
                    continue

                m = re.search("^(?P<word>[a-zA-Z0-9_'-]+)(?P<rest>.+)$", form, re.I)
                if m:
                    # 不可信, 这个类别
                    #f_dump.write("?4,"+word+","+pos+","+m.group('word').strip()+","+m.group('rest').strip()+"\n")
                    continue

                #f_dump.write("?5,"+word+","+pos+","+form+"\n")
                continue
            else:
                # 其他的直接输出词义
                f_dump.write(word+"|||"+lang+"|||"+pos+"|||"+html+"\n")
                pass

            #print(word)
        except Exception as e:
            print(line+str(e))
            return


    f_input.close()
    f_dump.close()

parse_csv_6()

pattern.append("superlative form of")
pattern.append("comparative form")

#parse_csv_5()
def parse_csv_7():
    
    word_dict = {}
    form_dict = {}
    f_dump = open("d:\\enwiktionary_en_20200106.json", 'w', -1, encoding="utf_8_sig")
    f_input = open("d:\\enwiktionary_en_20200106_with_form.csv", 'r', -1, encoding="utf_8_sig")
    
    for line in f_input:
        line = line.strip()
        # 空行
        if len(line)<1: continue

        try:
            m= re.search("^(?P<word>.+)[|]{3}(?P<lang>.+)[|]{3}(?P<pos>.+)[|]{3}(?P<definition>.*)([|]{3}(?P<rest1>.*)([|]{3}(?P<rest2>.*))?)?$", line)
            # 分析词的变形

            word = m.group("word")
            word = word.replace("_", " ")
            word = word.strip()
            lang = m.group("lang")
            pos  = m.group("pos")
            html = m.group("definition")
            rest1 = m.group("rest1")
            rest2 = m.group("rest2")
            
            if re.search('English', lang, re.I) is None:    continue
            
            if pos in pattern:
                original_word = html
                word_info = None
                if form_dict.get(original_word) is None:
                    word_info = {}
                    form_dict[original_word] = word_info
                word_info = form_dict[original_word]
                if word_info.get(pos) is None:
                    word_info[pos] = []
                word_info[pos].append(word)
                if rest1:
                    word_info[pos].append(word)
            else:
            
                word_info = None
                if word_dict.get(word+pos) is None:
                    word_info = {}
                    word_dict[word+pos] = word_info
                word_info = word_dict[word+pos]
                
                word_info['word'] = word
                word_info['pos'] = pos
                word_info['source'] = 'wiktionary'
                if word_info.get('definition') is None:
                    word_info['definitions'] = []
                word_info['definitions'].append(html)

            #print(word)
        except Exception as e:
            print(line+str(e))
            return
            
    # 查找变形信息
    for k, word_info in word_dict.items():
        word = word_info['word']
        if form_dict.get(word):
            word_info['form'] = form_dict.get(word)
            for x, y in word_info['form'].items():
                f_dump.write(word_info['pos']+", "+x+"\n") 
            
    word_list = []
    for k, word_info in word_dict.items():
        word_info_l = {}
        word_info_l[word_info['word']] = word_info
        word_list.append(word_info_l)
            
    #j = json.dumps(word_list, sort_keys=True, indent=4, separators=(',', ': '))

    #f_dump.write(j)
    f_input.close()
    f_dump.close()

#parse_csv_7()