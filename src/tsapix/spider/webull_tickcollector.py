"""
Requirement: Open Webull Desktop terminal
"""


import pyautogui
import pytesseract
import time
import os
import re
import pandas as pd
import numpy as np
from tqdm import tqdm
import cv2
import multitasking as _multitasking

from IPython.display import clear_output

# # cropped_img = img[0:60, 0:900]
# _ohlcv_yyxx = [60, 120, 0, 900]
# # cropped_img = img[-100:, -510:-360]
# _time_yyxx = [-50, None, -500, -310]

_ohlcv_yyxx = [85, 120, 17, 900]
_time_yyxx = [-112, -62, -510, -200] #[-112, -62, -480, -260]


def mk_screenshot():
    # make screen shot of ohlcv
    # have adjusted area
    # save root was set in Mac shift+cmd+5 options
    pyautogui.hotkey('shift', 'command', '5')
    pyautogui.hotkey('enter')

def drag_back_one_tick(_base_point=(1350, 220), _tick_gap=8):
    pyautogui.click(_base_point)
    pyautogui.mouseDown(_base_point, button='left')
    pyautogui.dragTo(_base_point[0]+_tick_gap, _base_point[1], button='left')

def re_identify_sid(fname):
    sid = "".join(
        re.findall("[0-9]", 
        re.findall("[0-9]{4}-[0-9]{2}-[0-9]{2} at [0-9]{2}.[0-9]{2}.[0-9]{2}", fname)[0]))
    return sid

# def re_identify_ohlcv_elements(ohlcvstr):
#     elements = re.findall("[.0-9%-]+", ohlcvstr.replace(",", ""))
#     elements = [e for e in elements if len(e)>1]
#     return elements
def re_identify_ohlcv_elements(ohlcvstr):
    elements = re.findall("([-]{,1}[0-9]+[.][0-9]{2}[%]{,1})", ohlcvstr.replace(",", ""))
    elements = [e for e in elements if len(e)>1]
    return elements

# def re_identify_timestr(time_str):
#     time_str = re.findall("[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}", time_str)[0]
#     return time_str
def re_identify_timestr(time_str):
    time_str = re.findall("([0-9]{2}/[0-9]{2})[ ]{,1}([0-9]{2}:[0-9]{2})", time_str)[0]
    time_str = " ".join(time_str)
    time_str = re.findall("[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}", time_str)[0]
    return time_str

def dispatch_ohlcv_time(
        froot, 
        distfname='str.csv',
        recordstr=True,
        multi=True,
        _flder_suffix_dict = {
        'origin': 'origin/',
        'ohlcv': 'ohlcv/',
        'timelog': 'timelog/',
        'processed': 'bin/'
    }):
    fs = [f for f in os.listdir(froot + _flder_suffix_dict['origin']) if ".png" in f]
    if multi:
        for fname in tqdm(fs):
            try:
                dispatch_ohlcv_time_multi(fname, froot, distfname, recordstr, _flder_suffix_dict)
            except:
                time.sleep(10)
                dispatch_ohlcv_time_multi(fname, froot, distfname, recordstr, _flder_suffix_dict)

    else:
        for fname in tqdm(fs):
            dispatch_ohlcv_time_solo(fname, froot, distfname, recordstr, _flder_suffix_dict)
    return 

def dispatch_ohlcv_time_solo(
        fname,
        froot, 
        distfname='str.csv',
        recordstr=True,
        _flder_suffix_dict = {
        'origin': 'origin/',
        'ohlcv': 'ohlcv/',
        'timelog': 'timelog/',
        'processed': 'bin/'
    }, _ohlcv_yyxx=_ohlcv_yyxx, _time_yyxx=_time_yyxx):
    imgpath = froot + _flder_suffix_dict['origin'] + fname
    img = cv2.imread(imgpath)
    # ohlcv
    ohlcv_root = froot + _flder_suffix_dict['ohlcv']
    # cropped_img = img[0:60, 0:900]
    cropped_img = img[_ohlcv_yyxx[0]:_ohlcv_yyxx[1], _ohlcv_yyxx[2]:_ohlcv_yyxx[3]]
    cv2.imwrite(ohlcv_root+fname, cropped_img)
    # time
    time_root = froot + _flder_suffix_dict['timelog']
    # cropped_img = img[-100:, -510:-360]
    cropped_img = img[_time_yyxx[0]:_time_yyxx[1], _time_yyxx[2]:_time_yyxx[3]]
    cv2.imwrite(time_root+fname, cropped_img)

    if recordstr:
        try:
            record_str_from_ohlcv_time(froot, fname, distfname=distfname, _flder_suffix_dict=_flder_suffix_dict)
        except Exception as e:
            print(imgpath, e)
            
    return 

@_multitasking.task
def dispatch_ohlcv_time_multi(fname, froot, distfname, recordstr, _flder_suffix_dict):
    dispatch_ohlcv_time_solo(fname, froot, distfname, recordstr, _flder_suffix_dict)

def record_str_from_ohlcv_time(froot, fname, distfname, _flder_suffix_dict):
    time_root = froot + _flder_suffix_dict['timelog']
    ohlcv_root = froot + _flder_suffix_dict['ohlcv']

    time_str = screenshot_to_str(time_root+fname).replace("\n", "")
    time_str = re_identify_timestr(time_str)
    _date, _time = time_str.split(" ")

    move_from_a_to_b(froot + _flder_suffix_dict['origin'], froot + _flder_suffix_dict['processed'], fname)
    sid = re_identify_sid(fname)
    screenshot_to_strfile(ohlcv_root+fname, sid=sid, distfroot=froot, distfname=distfname, additional_cols=[_date, _time])
    return 

def record_str_from_full(froot, fname, distfname, _flder_suffix_dict,):
    full_root = froot + _flder_suffix_dict['processed']

    sid = re_identify_sid(fname)
    fullscreenshot_to_strfile(full_root+fname, sid=sid, distfroot=froot, distfname=distfname, )
    # move_from_a_to_b(froot + _flder_suffix_dict['origin'], froot + _flder_suffix_dict['processed'], fname)
    return 

# def dispatch_ohlcv_time_and_recordstrfile(froot, distfname="str.csv"):
#     fname = None
#     while fname is None:
#         try:
#             fname = [f for f in os.listdir(froot) if ".png" in f][0]
#         except:
#             time.sleep(1)
#     imgpath = froot + fname
#     img = cv2.imread(imgpath)
#     # ohlcv
#     ohlcv_root = froot + "ohlcv/"
#     cropped_img = img[0:60, 0:900]
#     cv2.imwrite(ohlcv_root+fname, cropped_img)
#     # ohlcv_str = screenshot_to_str(ohlcv_root+fname)
#     # time
#     time_root = froot + "timelog/"
#     cropped_img = img[-100:, -510:-360]
#     cv2.imwrite(time_root+fname, cropped_img)
#     time_str = screenshot_to_str(time_root+fname).replace("\n", "")
#     time_str = re_identify_timestr(time_str)
#     _date, _time = time_str.split(" ")

#     move_from_a_to_b(froot, froot + "origin/", fname)
#     sid = re_identify_sid(fname)
#     screenshot_to_strfile(ohlcv_root+fname, sid=sid, distfroot=froot, distfname=distfname, additional_cols=[_date, _time])
#     return 

def screenshot_to_str(img_path, ):
    return pytesseract.image_to_string(img_path)

def screenshot_to_strfile(img_path=None, sid='',
        distfroot="/Users/my/Documents/webull_tick_imags/20250101TSLA/", 
        distfname="str.csv", additional_cols=[]):
    xstr = screenshot_to_str(img_path)
    elements = re_identify_ohlcv_elements(xstr)
    elements.extend(additional_cols)
    elementstr = sid + "," + ",".join(elements) + '\n'
    with open(distfroot+distfname, 'a') as distf:
        distf.write(elementstr)

def re_identify_ohlcv_elements_full(ohlcvstr):
    elements = re.findall("[0OHLCV] ([0-9]{3}[.][0-9]{2})|([-+][0-9]+[.][0-9]{2}[%]{,1})|Vol ([0-9,]+)", ohlcvstr.replace(",", ""))
    from functools import reduce
    _e = reduce(lambda x,y: x+y, elements)
    elements = [e.replace("+", "") for e in _e if len(e)>1]
    timestr = re_identify_timestr(ohlcvstr)
    elements.extend(timestr.split(" "))
    return elements

def fullscreenshot_to_strfile(img_path=None, sid='',
        distfroot="/Users/my/Documents/webull_tick_imags/20250101TSLA/", 
        distfname="str.csv", ):
    xstr = screenshot_to_str(img_path)
    elements = re_identify_ohlcv_elements_full(xstr)
    elementstr = sid + "," + ",".join(elements) + '\n'
    with open(distfroot+distfname, 'a') as distf:
        distf.write(elementstr)
    
def imgfolder_to_strfile(
        img_root="/Users/my/Documents/webull_tick_imags/20250101TSLA/ohlcv/", 
        distfroot="/Users/my/Documents/webull_tick_imags/20250101TSLA/", distfname="str.csv", dispose=False):
    fs = [f for f in os.listdir(img_root) if ".png" in f]
    for f in tqdm(fs):
        sid = re_identify_sid(f)
        screenshot_to_strfile(img_root+f, sid, distfroot, distfname)
        if dispose:
            move_from_a_to_b(img_root, distfroot+"bin/", f)
            
def move_from_a_to_b(aroot, broot, ffullname):
    import shutil
    shutil.move(aroot+ffullname, broot+ffullname)


class TickCollector:
    def __init__(self, 
                 distfroot=None, 
                 distfname=None,
                 targetticknum=1000,
                 _base_point=(1350, 220), 
                 _tick_gap=8,
                 _flder_suffix_dict={
                    'origin': 'origin/',
                    'ohlcv': 'ohlcv/',
                    'timelog': 'timelog/',
                    'processed': 'bin/'
                }
            ):
        self.distfroot = distfroot
        self.distfname = distfname
        self.targetticknum = targetticknum
        self._flder_suffix_dict = _flder_suffix_dict
        
        self._base_point = _base_point
        self._tick_gap = _tick_gap

        self.doneticknum = 0

    def backtracker(self, flydispose=False, bucknum=50):
        self.img_root = self.distfroot + 'ohlcv/'
        self.flydispose = flydispose
        self.bucknum = bucknum
        self._done_bucks = 0
        self._total_bucks = int(np.ceil(self.targetticknum / self.bucknum))
        while self.doneticknum<self.targetticknum:
            self._backtracker_eachbuck()
            self._done_bucks += 1

    def _backtracker_eachbuck(self):
        # collect ticks
        print("Collecting ticks...")
        self.i = 0
        for i in tqdm(range(self.bucknum)):
            if self.doneticknum<self.targetticknum:
                self.update_state()
                self._screenshot()
                self.doneticknum+=1
                self.i += 1
                time.sleep(2)
        # imgs to strfile
        print("Transforming images...")
        imgfolder_to_strfile(img_root=self.img_root, 
            distfroot=self.distfroot, distfname=self.distfname, dispose=self.flydispose)
        
    # def flytracker(self):
    #     while self.doneticknum<self.targetticknum:
    #         self.update_state(buck=False)
    #         self._screenshot()
    #         dispatch_ohlcv_time_and_recordstrfile(self.distfroot, distfname=self.distfname)
    #         self.doneticknum += 1
    #         time.sleep(2)

    def pure_dispatch_ohlcv_time(self, multi=True):
        dispatch_ohlcv_time(
            froot=self.distfroot,
            distfname=self.distfname,
            recordstr=True,
            multi=multi,
            _flder_suffix_dict=self._flder_suffix_dict,
        )
        restnum = 100
        while restnum!=0:
            restnum = len([f for f in os.listdir(self.distfroot + self._flder_suffix_dict['origin']) if ".png" in f])
            clear_output(wait=True)
            print("{} image/s remain to be processed...".format(restnum))
        print('Done')
        return
    
    def pure_screenshot(self, sleep=1):
        while self.doneticknum<self.targetticknum:
            self.update_state(buck=False)
            self._screenshot()
            self.doneticknum += 1
            time.sleep(sleep)

    def _screenshot(self, ):
        drag_back_one_tick(_base_point=self._base_point, _tick_gap=self._tick_gap)
        mk_screenshot()
        
    def update_state(self, buck=False):
        clear_output(wait=True)
        if buck:
            print("[", "*"*self._done_bucks, "-"*(self._total_bucks-self._done_bucks), "]", "{:.2f}% Done".format(self._done_bucks/self._total_bucks), "{} ticks Done".format(self.doneticknum))
            print("|", "*"*self.i, "-"*(self.bucknum-self.i), "|")
        else:
            print("{} ticks Done".format(self.doneticknum))
            print("|", "*"*self.doneticknum, "-"*(self.targetticknum-self.doneticknum), "|")
    

