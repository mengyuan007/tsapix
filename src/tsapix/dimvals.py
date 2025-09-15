from tsapix.utils import icloud_froot, cube_warehouse_root

from tsapix.spider.base import load_cube_n_axes, get_dtbk, load_maps
from tsapix.utils import nan_argsort

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

cuberoot=cube_warehouse_root

dtformatdict={
            'd': "%Y-%m-%d",
            'w': "%Y-%m-%d",
            'm': "%Y-%m-%d",
            '5min': "%Y-%m-%d %H:%M",
            '15min': "%Y-%m-%d %H:%M",
            '30min': "%Y-%m-%d %H:%M",
            '60min': "%Y-%m-%d %H:%M",
        }

maps = load_maps()
code_name_mapdict = maps['stock_meta']

# def maps():
#     return tsapi.base.load_maps()


def load_histpx_cubes(
    fts=[
        ('5min', 'bfq'),
        ('d', 'bfq'),
        ('d', 'hfq'),
        ('d', 'qfq'),
    ],
    cuberoot=cuberoot,
    dtformatdict=dtformatdict,
):
    """ Load histpx cube and axes.

    fts: list of tuple (frequency, px type)
    cuberoot: string, cube file save root
    dtformatdict: dict, indicate time format for different frequency
    """
    histpx = {}
    for frq, tp in fts:
        _k = f'{frq}_{tp}'
        print("Loading ", _k, "... ", end=" ")

        histpx[_k]={}
        cube_dict = load_cube_n_axes(f'histpx_{_k}', froot=cuberoot, timeformat=dtformatdict[frq])
        _cube = cube_dict['cube']
        _axs = cube_dict['axes']
        histpx[_k]['cube'] = _cube
        histpx[_k]['axes'] = _axs

        for fld in _axs[0]:
            print(fld, end="; ")
            histpx[_k][fld] = pd.DataFrame(
                                    _cube[_axs[0].index(fld), :, :], 
                                    index=_axs[1], 
                                    columns=_axs[2]).ffill()
        print()
    return histpx

def get_boll_lines(
    pxpd,
    _w=20,
    _nstd=2,
):
    """ Calculate BOLL elements.

    pxpd: DataFrame, price for calculate BOLL
    _w: int, rolling window
    _nstd: int / float, times of std add on / subtruct from mean
    
    """
    _mean = pxpd.copy(deep=True).rolling(_w).mean()
    _std = pxpd.copy(deep=True).rolling(_w).std()

    _upper_bond = _mean + _nstd * _std
    _lower_bond = _mean - _nstd * _std
    return {
        'px': pxpd,
        'm': _mean,
        's': _std,
        'u': _upper_bond,
        'l': _lower_bond,
        '%b': (pxpd - _lower_bond) / (_upper_bond - _lower_bond)
    }

def get_rchgs(
    chgpd,
):
    """ Calculate relative percentage change strength.
    
    chgpd: DataFrame, price percent change
    """
    pchgspd = pd.DataFrame(
        chgpd.apply(lambda x: nan_argsort(x, ascending=False), axis=1).to_list(), 
        index=chgpd.index,
        columns=chgpd.columns
    )

    _d = pchgspd.max(axis=1).values
    pchgspd_01 = pchgspd.apply(lambda x: x/_d)
    return {
        'rank': pchgspd.copy(deep=True),
        '01': pchgspd_01.copy(deep=True)
    }

def daily_intraday_toprchg(histpx, ft='5min_bfq', topn=20):
    """ Times ranked top; return daily frequency.

    histpx: dict, output of load_histpx_cubes
    ft: string, indicate frequency and price type
    topn: int, threshold for consideration as top
    """
    chgpd = 100 * ((histpx[ft]['High'] / histpx[ft]['Close'].shift(1)) - 1)
    rchgs = get_rchgs(chgpd)
    dbk = get_dtbk(chgpd.index[0].strftime("%Y-%m-%d"), chgpd.index[-1].strftime("%Y-%m-%d"), 'd')
    toprchg = dbk.join((rchgs['rank'] < topn).resample('d').sum())
    return toprchg

def add_rel_rel01(xdict, _ks):
    for k in _ks:
        xdict[f"{k}_rel"] = pd.DataFrame(
            xdict[k].copy(deep=True).apply(lambda x: nan_argsort(x, ascending=False), axis=1).to_list(), 
            index=xdict[k].index,
            columns=xdict[k].columns
        )
        _d = xdict[f"{k}_rel"].max(axis=1).values
        xdict[f"{k}_rel01"] = xdict[f"{k}_rel"].apply(lambda x: x/_d)
    return xdict

def toprchg_indicators(toprchg):
    """ Indicators based on toprchg.

    toprchg: DataFrame, output of daily_intraday_toprchg
    
    """
    res = {
        'v1': (toprchg>0).rolling(5).sum()>3,
        'v2': (toprchg>0).rolling(20).mean(),
        'v3': toprchg.rolling(20).sum(),
    }

    res = add_rel_rel01(res, _ks=['v2', 'v3'])
    return res