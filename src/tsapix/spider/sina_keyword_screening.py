import requests
import json
import time
import  re
# import pymssql
# import pymysql
import  datetime
import random
from requests.adapters import HTTPAdapter
import pandas as pd
import numpy as np
from functools import reduce
import matplotlib.pyplot as plt

datapath = "./"

import logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename=f'{datapath}sina_hourlyupdates.log', level=logging.DEBUG, format=LOG_FORMAT)


class Colour:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def screening_keywords(keyword=''):
    page = 0
    while True:
        try:
            page+=1
            referer_url = "http://finance.sina.com.cn/7x24/?tag=0"
            cookie = "UOR=www.baidu.com,tech.sina.com.cn,; SINAGLOBAL=114.84.181.236_1579684610.152568; UM_distinctid=16fcc8a8b704c8-0a1d2def9ca4c6-33365a06-15f900-16fcc8a8b718f1; lxlrttp=1578733570; gr_user_id=2736e487-ee25-4d52-a1eb-c232ac3d58d6; grwng_uid=d762fe92-912b-4ea8-9a24-127a43143ebf; __gads=ID=d79f786106eb99a1:T=1582016329:S=ALNI_MZoErH_0nNZiM3D4E36pqMrbHHOZA; Apache=114.84.181.236_1582267433.457262; ULV=1582626620968:6:4:1:114.84.181.236_1582267433.457262:1582164462661; ZHIBO-SINA-COM-CN=; SUB=_2AkMpBPEzf8NxqwJRmfoWz2_ga4R2zQzEieKfWADoJRMyHRl-yD92qm05tRB6AoTf3EaJ7Bg2UU4l1CDZXUBCzEuJv3mP; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhqhhGsPWdPjar0R99pFT8s"
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Cookie": cookie,
                "Host": "zhibo.sina.com.cn",
                "Referer": referer_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
            }
            base_url = "http://zhibo.sina.com.cn/api/zhibo/feed?callback=jQuery0&page=%s"%page+"&page_size=20&zhibo_id=152&tag_id=0&dire=f&dpc=1&pagesize=20&_=0%20Request%20Method:GET%27"
            data = get_json_data(base_url,headers)
            
            time.sleep(10)
            print("+", end=' ')
        except Exception as e:
            print('error', e)
            continue
            
def get_json_data(base_url,headers):
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
 
    try:
        response = requests.get(base_url, timeout=5, headers=headers)
        html = response.text
        # print(html)
        html_cl = html[12:-14]
        false = False
        true = True
        null = None
        html_json = eval(html_cl)
        json_str = json.dumps(html_json)
        results = json.loads(json_str)
        data = results['result']['data']['feed']['list']
    except Exception as e:
        print('get_json_str未收录错误类型，请检查网络通断,错误位置：',e)
        time.sleep(5)
        get_json_data(base_url, headers)
    else:
        return data
    
def get_info_from_json(jsonlist):
    _resdict = {
        "id": [],
        "txt": [],
        "time": [],
    }
    _tradable = {
        "market": [],
        "symbol": [],
        "key": [],
        "id": []
    }
    for d in jsonlist:
        _resdict["id"].append(d["id"])
        _resdict["txt"].append(d["rich_text"])
        _resdict["time"].append(d["create_time"])
        try:
            _ext = json.loads(d['ext'])
            if len(_ext['stocks'])>0:
                for s in _ext['stocks']:
                    _tradable['market'].append(s['market'])
                    _tradable['symbol'].append(s['symbol'])
                    _tradable['key'].append(s['key'])
                    _tradable['id'].append(d["id"])
        except Exception as e:
            logging.error(e)
    return _resdict, _tradable


class ScreeningKeyword:
    
    def __init__(self):
        self.news_bag = []
    
    def screening_keywords(self, keyword='', record_target=100, start_page=0, time_limit='2010-03-19 18:38:45'):
        page = start_page
        while True:
            try:
                page+=1
                referer_url = "http://finance.sina.com.cn/7x24/?tag=0"
                cookie = "UOR=www.baidu.com,tech.sina.com.cn,; SINAGLOBAL=114.84.181.236_1579684610.152568; UM_distinctid=16fcc8a8b704c8-0a1d2def9ca4c6-33365a06-15f900-16fcc8a8b718f1; lxlrttp=1578733570; gr_user_id=2736e487-ee25-4d52-a1eb-c232ac3d58d6; grwng_uid=d762fe92-912b-4ea8-9a24-127a43143ebf; __gads=ID=d79f786106eb99a1:T=1582016329:S=ALNI_MZoErH_0nNZiM3D4E36pqMrbHHOZA; Apache=114.84.181.236_1582267433.457262; ULV=1582626620968:6:4:1:114.84.181.236_1582267433.457262:1582164462661; ZHIBO-SINA-COM-CN=; SUB=_2AkMpBPEzf8NxqwJRmfoWz2_ga4R2zQzEieKfWADoJRMyHRl-yD92qm05tRB6AoTf3EaJ7Bg2UU4l1CDZXUBCzEuJv3mP; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhqhhGsPWdPjar0R99pFT8s"
                headers = {
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "Cookie": cookie,
                    "Host": "zhibo.sina.com.cn",
                    "Referer": referer_url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
                }
                base_url = "http://zhibo.sina.com.cn/api/zhibo/feed?callback=jQuery0&page=%s"%page+"&page_size=20&zhibo_id=152&tag_id=0&dire=f&dpc=1&pagesize=20&_=0%20Request%20Method:GET%27"
                self.data = get_json_data(base_url,headers)
                self.related_data = [e for e in self.data if keyword in e['rich_text']]
                self.news_bag.extend(self.related_data)

                time.sleep(10)
                print("@", page, self.data[-1]['update_time'], end=' ')
                print("News Bag Length: ", len(self.news_bag), "/", record_target)
                
                if len(self.news_bag) >= record_target:
                    print('Reach target limit... Exit')
                    break
                    
                if self.data[-1]['update_time'] < time_limit:
                    break
                    
            except Exception as e:
                print('error', e)
                continue
                
            except KeyboardInterrupt:
                break
                
                

def normal_task_process(keyword='加沙', record_target=100, start_page=0, time_limit='2010-03-19 18:38:45'):
    xobj = ScreeningKeyword()
    xobj.screening_keywords(keyword=keyword, record_target=record_target, start_page=start_page, time_limit=time_limit)

    try:
        _resdict, _tradable = get_info_from_json(xobj.news_bag)
        # pd.DataFrame(_resdict).sort_values('id')
        return _resdict
    except Exception as e:
        print("Error... Returning xobj, use xobj.news_bag to check results.")
        return xobj