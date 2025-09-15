import os
import sys

# # icloud_froot = "/Users/{}/Library/Mobile Documents/com~apple~CloudDocs/".format(os.environ['USER'])
# icloud_froot = "/Users/{}/Documents/anaconda/anaconda3/lib/python3.11/site-packages/tsapi/_local/".format(os.environ['USER'])
# # sys.path.insert(0, icloud_froot + "/env/pkgs")

icloud_froot = "/Users/{}/Documents/pypi_projects/tsapix/_local/".format(os.environ['USER'])

env_db_root = icloud_froot + "env/data/"
cube_warehouse_root = icloud_froot + "env/data/cube/"
_log_froot = icloud_froot + "/env/log/"

env_raw_root = icloud_froot + "env/data/raw/"

code_univ_save_path = env_db_root + 'a_code_univ.yaml'

import requests
import json

import os
from typing import Dict, List
import pandas as pd
import numpy as np
import ruamel_yaml as yaml
import pyarrow.parquet as pq
import logging
import logging.config

from datetime import date

import numpy as np
import pandas as pd
import multitasking as _multitasking
import pandas_market_calendars as mcal

import pandas as _pd
import numpy as _np
import sys as _sys

def empty_df(index=None, cols=[], index_name=None):
    if index is None:
        index = []
    empty = _pd.DataFrame(index=index, data={c:_np.nan for c in cols})
    if index_name:
        empty.index.name = index_name
    return empty


class ProgressBar:
    def __init__(self, iterations, text='completed'):
        self.text = text
        self.iterations = iterations
        self.prog_bar = '[]'
        self.fill_char = '*'
        self.width = 50
        self.__update_amount(0)
        self.elapsed = 1

    def completed(self):
        if self.elapsed > self.iterations:
            self.elapsed = self.iterations
        self.update_iteration(1)
        print('\r' + str(self), end='', file=_sys.stderr)
        _sys.stderr.flush()
        print("", file=_sys.stderr)

    def animate(self, iteration=None):
        if iteration is None:
            self.elapsed += 1
            iteration = self.elapsed
        else:
            self.elapsed += iteration

        print('\r' + str(self), end='', file=_sys.stderr)
        _sys.stderr.flush()
        self.update_iteration()

    def update_iteration(self, val=None):
        val = val if val is not None else self.elapsed / float(self.iterations)
        self.__update_amount(val * 100.0)
        self.prog_bar += f"  {self.elapsed} of {self.iterations} {self.text}"

    def __update_amount(self, new_amount):
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
        pct_place = (len(self.prog_bar) // 2) - len(str(percent_done))
        pct_string = f'{percent_done}%%'
        self.prog_bar = self.prog_bar[0:pct_place] + (pct_string + self.prog_bar[pct_place + len(pct_string):])

    def __str__(self):
        return str(self.prog_bar)


def save_as_yaml(yaml_path, content):
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(content, f, Dumper=yaml.RoundTripDumper)

def read_yaml_file(yaml_path):
    with open(yaml_path, "r") as f:
        yaml_dict = yaml.load(f.read(), Loader=yaml.Loader)
    return yaml_dict

def pq_file_to_pd(fpath):
    return pq.read_table(fpath).to_pandas()

def update_yaml(yaml_path, newpart, unique=False):
    try:
        histpart = read_yaml_file(yaml_path)
        if type(histpart) is List:
            newpart = histpart.extend(newpart)
            if unique:
                newpart = list(set(newpart))
        elif type(histpart) is Dict:
            newpart.update(histpart)
    except Exception as e:
        print(e)
        pass
    print("update_yaml  ", yaml_path)
    save_as_yaml(yaml_path, newpart)

def save_npcube(fpath, xcube):
    if ".npy" in fpath:
        np.save(fpath, xcube)
    elif ".npz" in fpath:
        np.savez_compressed(fpath, xcube)

def read_npcube(fpath):
    if ".npy" in fpath:
        return np.load(fpath)
    elif ".npz" in fpath:
        return np.load(fpath)['arr_0']

def nan_argsort(x, ascending=True):
    _mask = np.isnan(x.values)
    _argx = np.argsort(np.argsort(x.values[~_mask]))
    if not ascending:
        _argx = len(_argx) - _argx
    _x = x.values
    _x[~_mask] = _argx
    return _x

def initiate_logger(logfname, logfroot="", xlevel=logging.DEBUG):
    logging.basicConfig(filename=f"{logfroot}{logfname}.log", level=xlevel, 
                        format='%(asctime)s - %(levelname)s - %(message)s'
                        )
    return logging.getLogger(f"{logfroot}{logfname}.log")

def initiate_logger_v2(logfname, logfroot="", xlevel=logging.DEBUG, fmode='a'):
    logging.basicConfig(level=xlevel, 
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(filename=f"{logfroot}{logfname}.log", mode=fmode)
                        ]
                        )
    return logging.getLogger(f"{logfroot}{logfname}.log")

def save_cube_n_axes(xcube, xaxes, fname, save_root=None):
    save_npcube(f"{save_root}/{fname}.npz", xcube)
    save_as_yaml(f"{save_root}/{fname}.yaml", xaxes)
    
def load_cube_n_axes(pairname=None, froot=None, timeformat="%Y-%m-%d %H:%M"):
    xcube = read_npcube(f"{froot}/{pairname}.npz")
    xaxes = read_yaml_file(f"{froot}/{pairname}.yaml")
    xaxes[1] = pd.to_datetime(xaxes['1str'], format=timeformat)
    return {
        'cube': xcube,
        'axes': xaxes,
    }
