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

def daily_sina_limit_notice():
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
    
def find_pngurl(data):
    for e in data:
        if '涨停分析' in e['rich_text']:
    #         pngurl=e['multimedia']['img_url'][0]
            return e['multimedia']['img_url'][0]
    return None
        
def get_and_save_png(pngurl, savename):
    import urllib
    urllib.request.urlretrieve(pngurl.replace('\\', ''), "./{}.png".format(savename))

def mail_outlook(filepathlist, subject="Sina Hourly Updates"):
    """
    https://djangocentral.com/sending-emails-with-csv-attachment-using-python/
    https://stackoverflow.com/questions/23171140/how-do-i-send-an-email-with-a-csv-attachment-using-python
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage

    frommail="mydotu@outlook.sg"
    tomail="tan.mengyuan@uobgroup.com"
    password="Tmy07121997"

    msg=MIMEMultipart()
    msg["From"]=frommail
    msg["To"]=tomail
    msg["Subject"]=subject
    body_part = MIMEText("Hi, Attached hourly Sina News...", 'plain')
    
    msg.attach(body_part)
    for fpath in filepathlist:
        with open(fpath, 'rb') as f:
            if ".csv" in fpath:
                _attach = MIMEApplication(f.read(), Name=fpath.split("/")[-1])
            elif ".png" in fpath:
                _attach = MIMEImage(f.read(), Name=fpath.split("/")[-1])
            else:
                pass
            msg.attach(_attach)
        
    server = smtplib.SMTP("smtp-mail.outlook.com", 587)
    # server = smtplib.SMTP("smtp.gmail.com:587")
    check = server.ehlo()
    server.starttls()
    server.login(frommail, password)
    server.sendmail(frommail, tomail, msg.as_string())
    server.quit()
    
def sina_web_common(page):
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
    base_url = "http://zhibo.sina.com.cn/api/zhibo/feed?callback=jQuery0&page=%s"%page+"&page_size=100&zhibo_id=152&tag_id=0&dire=f&dpc=1&pagesize=20&_=0%20Request%20Method:GET%27"
    return base_url,headers
    
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

def hourly_updates(ps=[1,2,3,4], send_mail=True):
    respd, tradablepd = get_hourly_datapd(ps=ps)
    respd.to_csv(f"{datapath}sina_news_txt.csv", index=False)
    tradablepd, keycount = process_tradablepd(tradablepd)
    tradablepd.to_csv(f"{datapath}sina_news_tradable.csv", index=False)
    keycount.to_frame().to_csv(f"{datapath}keycount.csv",)
    
    filepathlist = [
        f"{datapath}sina_news_txt.csv",
        f"{datapath}sina_news_tradable.csv",
        f"{datapath}keycount.csv"
    ]
    if send_mail:
        mail_outlook(filepathlist, subject="Sina Updates")
    else:
        return respd, tradablepd, keycount.to_frame()

def get_hourly_datapd(ps=[1,2,3,4]):
    resdicts = []
    tradabledicts = []
    for page in ps:
        base_url, headers = sina_web_common(page)
        jsonlist = get_json_data(base_url, headers)
        try:
            assert len(jsonlist)==100
        except:
            logging.warning("Return records number less than 100...")
        _resdict, _tradable = get_info_from_json(jsonlist)
        resdicts.append(_resdict)
        if len(_tradable['symbol'])==0:
            logging.info("No tradable records...")
        else:
            tradabledicts.append(_tradable)
    respd = pd.concat([pd.DataFrame(x) for x in resdicts]).sort_values("id")
    tradablepd = pd.concat([pd.DataFrame(x) for x in tradabledicts]).sort_values("id")
    return respd[["id", "time", "txt"]], tradablepd[["id", "market", "symbol", "key"]]

def process_tradablepd(tradablepd):
    keycount = tradablepd.groupby("key").count()['id'].sort_values(ascending=False)
#     marketcount = tradablepd.groupby("market").count()['id'].sort_values(ascending=False)
    keycount.name="keycount"
#     marketcount.name="mktcount"
    tradablepd = tradablepd.set_index("key").join(keycount).sort_values("keycount", ascending=False).reset_index()
    tradablepd = tradablepd[['id', 'key', 'keycount', 'market', 'symbol']]
    return tradablepd, keycount
    