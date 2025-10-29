from .base import *
from .base import sz_identifier_0, a_code_univlist, china_tcalendar, icloud_froot
from . import shared
from . import utils

from tsapix.utils import env_db_root, _log_froot, env_raw_root

import multitasking as _multitasking
import time as _time
from datetime import datetime, timedelta
from functools import reduce
import logging


_log_froot = _log_froot
_log_fname = "eastmoney.log"
_logger = utils.initiate_logger(_log_fname.replace(".log", ""), _log_froot, xlevel=logging.INFO)

_logger.info("Touched EastMoney")

### ------------ API Endpoints ------------ 
_furl_dict = {
    'hist_px': """http://{}.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={}.{}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f61&klt={}&fqt={}&end={}&lmt={}&_=?""",
    'hist_cf': """https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?cb=&lmt=0&klt=101&fields1=f1%2Cf2%2Cf3%2Cf7&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61%2Cf62%2Cf63%2Cf64%2Cf65&ut=b2884a393a59ad64002292a3e90d46a5&secid={}.{}&_=?""",
    'bk_industry_cf': """https://push2.eastmoney.com/api/qt/clist/get?cb=&fid=f62&po=1&pz=100&pn=1&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13""",
    'bk_concept_cf': """https://push2.eastmoney.com/api/qt/clist/get?cb=&fid=f62&po=1&pz=500&pn=1&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fs=m%3A90+t%3A3&fields=f12%2Cf14%2Cf3%2Cf62""",
    'bk_geo_cf': """https://push2.eastmoney.com/api/qt/clist/get?cb=&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=b2884a393a59ad64002292a3e90d46a5&fs=m%3A90+t%3A1&fields=f12%2Cf14%2Cf3%2Cf62""",
    'xbk_names': """https://{}.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=1000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&dect=1&wbp2u=|0|0|0|web&fid=f3&fs=b:{}+f:!50&fields=f12,f14,f3,f62&_=""",


}

### ------------ Save Path ------------ 
# _save_root_base = f"/Users/{os.environ['USER']}/Documents/TS/data/"
# _save_root_base = "/Users/my/Documents/anaconda/anaconda3/lib/python3.11/site-packages/tsapi/_local/data/"
_save_root_base = env_db_root
# _save_root_base = icloud_froot + "/data/"
_save_root_dict = {
    '_base': _save_root_base,
    'hist_px_raw': _save_root_base+'raw/price/',
    'hist_px_raw_panel': _save_root_base+'raw/price/panel/',
    'hist_cf_raw': _save_root_base+'raw/cfhist/',
    'industry_bkcf_raw': _save_root_base+'raw/bkcf/industry/',
    'concept_bkcf_raw': _save_root_base+'raw/bkcf/concept/',
    'geo_bkcf_raw': _save_root_base+'raw/bkcf/geo/',
    'industry_bknames_raw': _save_root_base+'raw/industry/',
    'concept_bknames_raw': _save_root_base+'raw/concept/',
    'geo_bknames_raw': _save_root_base+'raw/geo/',
    'clouddb': icloud_froot + 'env/data/',
}

for k, v in _save_root_dict.items():
    os.makedirs(v, exist_ok=True)

_savepath_fstr_dict = {
    'hist_px_raw': _save_root_dict['hist_px_raw'] + "frq={}/{}/{}.yaml", #frq, pricetype, code
    'hist_px_raw_panel': _save_root_dict['hist_px_raw'] + "frq={}/{}/{}.csv", #frq, pricetype, code
    'hist_cf_raw': _save_root_dict['hist_cf_raw'] + "{}.yaml", #code

}

_savepath_fdict = {
    'bknames_perf_listdict': _save_root_dict['industry_bknames_raw'].replace("industry", "") + "bknames_perf.yaml",
    'histpx_cube': _save_root_dict['clouddb']+'histpx_cube.npy'
}

__all__ = [
    'HistPX',
    'HistCapitalFlow'
]

def get_dtbk(start, end, xfreq, 
        _freq_mapdict={
            'd': "D",
            'w': "W",
            'm': "M",
            '5min': "5min",
            '15min': "15min",
            '30min': "30min",
            '60min': "60min",
    }, tcalendar=china_tcalendar, ):
    trading_dates = [x.strftime("%Y-%m-%d") for x in tcalendar.valid_days(start_date=start, end_date=end)]
    _valid_list = pd.bdate_range(start, end, freq=_freq_mapdict[xfreq])

    if 'min' in xfreq or 's' in xfreq:
        # _in_trading_times
        _valid_list = [x for x in _valid_list if np.any([
            np.all([x.strftime("%H:%M:%S")<="15:00:00", x.strftime("%H:%M:%S")>="13:00:00"], axis=0),
            np.all([x.strftime("%H:%M:%S")<="11:30:00", x.strftime("%H:%M:%S")>="09:30:00"], axis=0),
        ], axis=0)]
    # _in_trading_dates
    _valid_list = [x for x in _valid_list if x.strftime("%Y-%m-%d") in trading_dates]
    
    if xfreq in ['w', 'm']:
        def _xdate(x):
            try:
                return x.index[-1].strftime("%Y-%m-%d")
            except:
                return np.nan
        _valid_list = list(pd.DataFrame({'dts': pd.to_datetime(trading_dates), 'dts0': pd.to_datetime(trading_dates)}).set_index('dts').resample(_freq_mapdict[xfreq]).apply(lambda x: _xdate(x)).dropna().values[:, 0])

    return pd.DataFrame({0:_valid_list}).set_index(0).sort_index()

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

# def update_cube(oldcube, oldcubeaxes, newcube, newcubeaxes):
#     # new dates
#     _newdateids = []
#     for i in range(len(newcubeaxes['1str'])):
#         if newcubeaxes['1str'][i] not in oldcubeaxes['1str']:
#             _newdateids.append(i)
#     # new tickers
#     _newtickerids = []
#     for i in range(len(newcubeaxes[2])):
#         if newcubeaxes[2][i] not in oldcubeaxes[2]:
#             _newtickerids.append(i)
#     # cube_newsec = newcube[:, _newids, :]


class HistPX:

    def __init__(self,
        frq, 
        pxtp,
        tickers,
        savepath_fstr=_savepath_fstr_dict['hist_px_raw'],
        dtformatdict={
            'd': "%Y-%m-%d",
            'w': "%Y-%m-%d",
            'm': "%Y-%m-%d",
            '5min': "%Y-%m-%d %H:%M",
            '15min': "%Y-%m-%d %H:%M",
            '30min': "%Y-%m-%d %H:%M",
            '60min': "%Y-%m-%d %H:%M",
        },
        start=None,
        end=None,
        lmt='1000000',
        apiend="20500101",
    ):
        self.frq = frq
        self.pxtp = pxtp
        self.tickers = tickers
        self.savepath_root = "/".join(savepath_fstr.format(frq, pxtp, '').split("/")[:-1])
        try:
            os.makedirs(self.savepath_root, exist_ok=True)
        except:
            pass
        self.savepath_fstr = savepath_fstr
        self.dtformat = dtformatdict[self.frq]
        self.start = start
        self.end = end
        # self.pdfreq = _freq_mapdict[frq]
        self.dtbk = get_dtbk(start, end, self.frq)
        self.lmt = lmt
        self.apiend = apiend
        pass

    def download(self, chunk_size=1000):
        try:
            _logger.info(f"Downloading {self.frq} {self.pxtp}...")
        except:
            pass

        _c = 0
        while _c < len(self.tickers):
            _sub_tickers = self.tickers[_c:_c+chunk_size]
            eastmoney_histpx_downloader(
                self.frq,
                self.pxtp,
                savepath_fstr=self.savepath_fstr,
                tickers=_sub_tickers,
                lmt=self.lmt,
                end=self.apiend,
            )
            _c += chunk_size
            _time.sleep(60)

        try:
            _logger.info(f"Download Done - {self.frq} {self.pxtp}")
        except:
            pass

    def get_cube(self, dtbk=None):
        dtbk = self.dtbk if dtbk is None else dtbk
        fs = [f for f in os.listdir(self.savepath_root) if f.replace(".yaml", "") in self.tickers]
        infopd_pool = {}
        for f in tqdm(fs):
            try:
                xcode = f.replace(".yaml", "")
                xpd = read_yaml_file(os.path.join(self.savepath_root, f))
                xpd = hist_px_json_to_panel(xpd, dtformat=self.dtformat)
                xpd = dtbk.join(xpd)
                infopd_pool[xcode] = xpd.copy(deep=True)
            except Exception as e:
                infopd_pool[xcode] = utils.empty_df(index=list(dtbk.index), 
                cols=['Open', 'Close', 'High', 'Low', 'TradeShares', 'TradeAmt', 'ZF', 'AbsChg', 'PctChg', 'TurnoverRate'])

        axsesinfo = {
            0: ['Open', 'Close', 'High', 'Low', 'TradeShares', 'TradeAmt', 'ZF', 'AbsChg', 'PctChg', 'TurnoverRate'],
            1: [x for x in dtbk.index],
            '1str': [x.strftime(self.dtformat) for x in dtbk.index],
            2: list(infopd_pool.keys())
        }
        xcube = np.stack([x.values for x in list(infopd_pool.values())])
        xcube = np.swapaxes(xcube, 0, -1)

        self.axsesinfo = axsesinfo
        self.xcube = xcube
        assert xcube.shape==(len(axsesinfo[0]), len(axsesinfo[1]), len(axsesinfo[2]))
        return axsesinfo, xcube

    def get_cube_and_save(self, dtbk=None, 
            pairname=None,
            froot=None,
        ):
        try:
            _logger.info(f"Forming Cube - {self.frq} {self.pxtp}")
        except:
            pass

        self.get_cube(dtbk)
        save_cube_n_axes(
            self.xcube, 
            {k:v for k,v in self.axsesinfo.items() if k!=1},
            pairname,
            save_root=froot,
        )

        try:
            _logger.info(f"Cube formed and saved - {self.frq} {self.pxtp}")
        except:
            pass

        return self.axsesinfo, self.xcube

    def load_cubedict(self, pairname=None, froot=None):
        return load_cube_n_axes(pairname, froot)


class HistCapitalFlow:

    def __init__(self,
        tickers,
        start=None,
        end=None,
        savepath_fstr=_savepath_fstr_dict['hist_cf_raw']
    ):
        self.tickers = tickers
        self.dtbk = get_dtbk(start, end, 'd')
        self.savepath_root = "/".join(savepath_fstr.format('').split("/")[:-1])
        self.dtformat = '%Y-%m-%d'
        pass

    def download(self, chunk_size=1000):
        _c = 0
        while _c < len(self.tickers):
            _sub_tickers = self.tickers[_c:_c+chunk_size]
            eastmoney_histcf_downloader(tickers=_sub_tickers)
            _c += chunk_size
            _time.sleep(60)

    def get_cube(self, dtbk=None):
        self.dtbk = self.dtbk if dtbk is None else dtbk
        fs = [f for f in os.listdir(self.savepath_root) if f.replace(".yaml", "") in self.tickers]
        infopd_pool = {}
        for f in tqdm(fs):
            try:
                xcode = f.replace(".yaml", "")
                xpd = read_yaml_file(os.path.join(self.savepath_root, f))
                xpd = [x.split(",") for x in xpd]
                xpd = pd.DataFrame(xpd)
                xpd = xpd.set_index(0)
                xpd.index = pd.to_datetime(xpd.index)
                xpd = xpd.astype(float)
                xpd = self.dtbk.join(xpd)
                infopd_pool[xcode] = xpd.copy(deep=True)
            except Exception as e:
                infopd_pool[xcode] = utils.empty_df(index=list(self.dtbk.index), 
                cols=['zljlr_je','xdjlr_je','zdjlr_je','ddjlr_je','cddjlr_je','zljlr_jzb','xdjlr_jzb','zdjlr_jzb','ddjlr_jzb','cddjlr_jzb','Close','PctChg','nan1','nan2'])

        axsesinfo = {
            0: ['zljlr_je','xdjlr_je','zdjlr_je','ddjlr_je','cddjlr_je','zljlr_jzb','xdjlr_jzb','zdjlr_jzb','ddjlr_jzb','cddjlr_jzb','Close','PctChg','nan1','nan2'],
            1: [x for x in self.dtbk.index],
            '1str': [x.strftime(self.dtformat) for x in self.dtbk.index],
            2: list(infopd_pool.keys())
        }
        
        for k, x in infopd_pool.items():
            print(x, x.values.shape)
        
        xcube = np.stack([x.values for x in list(infopd_pool.values())])
        xcube = np.swapaxes(xcube, 0, -1)

        self.axsesinfo = axsesinfo
        self.xcube = xcube
        assert xcube.shape==(len(axsesinfo[0]), len(axsesinfo[1]), len(axsesinfo[2]))
        return axsesinfo, xcube

    def get_cube_and_save(self, dtbk=None, 
            pairname=None,
            froot=None,
        ):
        self.get_cube(dtbk)
        save_cube_n_axes(
            self.xcube, 
            {k:v for k,v in self.axsesinfo.items() if k!=1},
            pairname,
            save_root=froot,
        )
        return self.axsesinfo, self.xcube

    def load_cubedict(self, pairname=None, froot=None):
        return load_cube_n_axes(pairname, froot)



#%% ### ------------ HistPX Functions ------------
def hist_px_url_processor(xurl, savepath=None):
    """ 
    Modify@20240727 - Process 5 min price data which has rolling loss... Protocal: append new data to hist; assume not update intraday
    """
    try:
        xpage = requests.get(xurl)
    except:
        _time.sleep(5)
        try:
            xpage = requests.get(xurl)
        except:
            pass
    xres = json.loads(xpage.text)
    if savepath is not None:
        os.makedirs("/".join(savepath.split("/")[:-1]), exist_ok=True)

        if "klt=5" in xurl or "klt=15" in xurl:
            try: # append new to hist instead replace all - for 5 min data
                hist_doc = read_yaml_file(savepath)
                hist_klines = hist_doc['data']['klines']
                hist_tms = sorted([x.split(",")[0] for x in hist_klines])
                _hist_latest = hist_tms[-1]

                new_klines = xres['data']['klines']
                real_new_klines = []
                for k in new_klines:
                    if k.split(",")[0] > _hist_latest:
                        real_new_klines.append(k)

                hist_doc['data']['klines'] = sorted(list(set(hist_klines + real_new_klines)), key=lambda x: x[:len(_hist_latest)])
                xres = hist_doc.copy()
            except FileNotFoundError:
                pass

        save_as_yaml(savepath, xres)
    # shared._DFS.append(xres)
    return xres
# def hist_px_url_processor(xurl, savepath=None):
#     try:
#         xpage = requests.get(xurl)
#     except:
#         _time.sleep(5)
#         try:
#             xpage = requests.get(xurl)
#         except:
#             pass
#     xres = json.loads(xpage.text)
#     if savepath is not None:
#         os.makedirs("/".join(savepath.split("/")[:-1]), exist_ok=True)
#         save_as_yaml(savepath, xres)
#     # shared._DFS.append(xres)
#     return xres

def hist_px_json_to_panel(xinfodict, dtformat="%Y-%m-%d %H:%M", ):
    xinfolist = xinfodict['data']['klines']
    xinfolist = [x.split(",") for x in xinfolist]
    xinfopd = pd.DataFrame(xinfolist)
    xinfopd.set_index(0, inplace=True)
    xinfopd.index = pd.to_datetime(xinfopd.index, format=dtformat)
    xinfopd = xinfopd[~xinfopd.index.duplicated(keep='first')]
    xinfopd = xinfopd.sort_index()

    xinfopd = xinfopd.astype(float)
    return xinfopd

def hist_px_url_processor_panel(ticker, xurl, dtformat="%Y-%m-%d %H:%M"):
    xpage = requests.get(xurl)
    xres = json.loads(xpage.text)
    # print("####", xres)
    try:
        _panel = hist_px_json_to_panel(xres, dtformat)
    except Exception as e:
        # shared._DFS[ticker] = utils.empty_df()
        # print(e)
        shared._DFS[ticker] = None
    else:
        shared._DFS[ticker] = _panel.copy(deep=True)

@_multitasking.task
def hist_px_url_processor_multi_panel(ticker, xurl, dtformat):
    hist_px_url_processor_panel(ticker, xurl, dtformat)
    shared._PROGRESS_BAR.animate()

def eastmoney_histpx_downloader_panellist(frq, pxtp, 
        startdate=None,
        enddate=None,
        histpx_furl=_furl_dict['hist_px'],
        kltmapdict={
            'd': "101",
            'w': "102",
            'm': "103",
            '5min': "5",
            '15min': "15",
            '30min': "30",
            '60min': "60",
        },
        fqtmapdict={
            'bfq': '0', # 不复权
            'qfq': '1', # 前复权
            'hfq': '2', # 后复权
        },
        end="20500101",
        lmt="1000000",
        tickers=a_code_univlist,
        dtformatdict={
            'd': "%Y-%m-%d",
            'w': "%Y-%m-%d",
            'm': "%Y-%m-%d",
            '5min': "%Y-%m-%d %H:%M",
            '15min': "%Y-%m-%d %H:%M",
            '30min': "%Y-%m-%d %H:%M",
            '60min': "%Y-%m-%d %H:%M",
        },
        dtbk=None
    ):
    xurl_list = [histpx_furl.format(
                        np.random.randint(100),
                        0 if xticker[0] in sz_identifier_0 else 1,
                        xticker,
                        kltmapdict[frq],
                        fqtmapdict[pxtp],
                        end,
                        lmt,
                    ) for xticker in tickers]
    shared._DFS = {}
    shared._PROGRESS_BAR = utils.ProgressBar(len(tickers), 'completed')
    _c = 0
    _multitasking.set_max_threads(max([len(tickers), _multitasking.cpu_count()*2]))
    while True:
        for ticker, xurl in list(zip(tickers, xurl_list))[_c:]:
            try:
                hist_px_url_processor_multi_panel(ticker, xurl, dtformat=dtformatdict[frq], progress=_c>0)
                _c+=1
            except RuntimeError:
                print("Can't start new thread, break restarting...", _c)
                _time.sleep(60)
                pass
        if _c==len(xurl_list):
            break
    
    while len(shared._DFS) < len(tickers):
        _time.sleep(0.01)

    shared._PROGRESS_BAR.completed()

    _axis2 = []
    _panels = []
    _freq_mapdict = {
        'd': "D",
        'w': "W",
        'm': "M",
        '5min': "5min",
        '15min': "15min",
        '30min': "30min",
        '60min': "60min",
    }
    dtbk = pd.DataFrame({0:pd.date_range(startdate, enddate, freq=_freq_mapdict[frq])}).set_index(0) if dtbk is None else dtbk
    for k, v in shared._DFS:
        if v is not None:
            _axis2.append(k)
            _panels.append(dtbk.join(v))
        else:
            print(k, "is None")
    return _axis2, _panels, shared._DFS

@_multitasking.task
def hist_px_url_processor_multi(xurl, savepath):
    hist_px_url_processor(xurl, savepath)
    # shared._PROGRESS_BAR.animate()

def eastmoney_histpx_downloader(frq, pxtp, 
        savepath_fstr=_savepath_fstr_dict['hist_px_raw'],
        histpx_furl=_furl_dict['hist_px'],
        kltmapdict={
            'd': "101",
            'w': "102",
            'm': "103",
            '5min': "5",
            '15min': "15",
            '30min': "30",
            '60min': "60",
        },
        fqtmapdict={
            'bfq': '0', # 不复权
            'qfq': '1', # 前复权
            'hfq': '2', # 后复权
        },
        end="20500101",
        lmt="1000000",
        tickers=a_code_univlist,
    ):
    save_path_list = [savepath_fstr.format(frq, pxtp, xticker) for xticker in tickers]
    xurl_list = [histpx_furl.format(
                        np.random.randint(100),
                        0 if xticker[0] in sz_identifier_0 else 1,
                        xticker,
                        kltmapdict[frq],
                        fqtmapdict[pxtp],
                        end,
                        lmt,
                    ) for xticker in tickers]

    # shared._DFS = []
    _c = 0
    _multitasking.set_max_threads(max([len(tickers), _multitasking.cpu_count()*2]))
    # shared._PROGRESS_BAR = utils.ProgressBar(len(tickers), 'completed')
    while True:
        for xurl, savepath in tqdm(list(zip(xurl_list, save_path_list))[_c:]):
            try:
                hist_px_url_processor_multi(xurl, savepath)
                _c+=1
            except RuntimeError:
                print("Can't start new thread, break restarting...", _c)
                _time.sleep(60)
                pass
        if _c==len(xurl_list):
            break

    # while len(shared._DFS) < len(tickers):
    #     _time.sleep(0.01)

    # shared._PROGRESS_BAR.completed()


#%% ### ------------ Hist CapitalFlow Functions ------------
def cfhist_processor(xticker, savepath_fstr=_savepath_fstr_dict['hist_cf_raw'], furl=_furl_dict['hist_cf']):
    mkt = '0' if xticker[0] in sz_identifier_0 else '1'
    xurl = furl.format(mkt, xticker)
    try:
        xres = requests.get(xurl)
    except:
        _time.sleep(5)
        try:
            xres = requests.get(xurl)
        except:
            shared._DFS.append(xticker)
            return 

    xdata = json.loads(xres.text)['data']['klines']
    fpath = savepath_fstr.format(xticker)
    try:
        hist_list = read_yaml_file(fpath)
        xdata += hist_list
        xdata = list(set(xdata))
    except:
        pass
    save_as_yaml(fpath, xdata)
    shared._DFS.append(xticker)
    return 
    
@_multitasking.task
def cfhist_processor_multi(xticker):
    cfhist_processor(xticker)
    shared._PROGRESS_BAR.animate()

def eastmoney_histcf_downloader(tickers):
    shared._DFS = []
    shared._PROGRESS_BAR = utils.ProgressBar(len(tickers), 'completed')
    for xticker in tickers:
        cfhist_processor_multi(xticker)

    while len(shared._DFS) < len(tickers):
        _time.sleep(0.01)
    shared._PROGRESS_BAR.completed()


#%% ### ------------ Industry / Concept / Geo Functions ------------
def eastmoney_industry_info_downloader():
    return eastmoney_xbk_info_downloader(xid='industry')

def eastmoney_concept_info_downloader():
    return eastmoney_xbk_info_downloader(xid='concept')

def eastmoney_geo_info_downloader():
    return eastmoney_xbk_info_downloader(xid='geo')

def eastmoney_xbk_info_downloader(
        xid='industry',
        chunk_size=100,
        light=False
        ):
    # 1. industry(xbk) universe
    bkcfpd, bkcode_list, bkcode_namemap = eastmoney_xbk_codeuniv_from_bkcf(xid=xid)
    if not light:
        # 2. names in each industry(xbk)
        # bknames_dict, code_namemap = eastmoney_each_xbk_info(bkcode_list, xid=xid)
        _c = 0
        while _c<len(bkcode_list):
            eastmoney_each_xbk_info_multi(bkcode_list[_c:_c+chunk_size], xid=xid)
            _c += chunk_size
            _time.sleep(60)
    return bkcfpd, bkcode_list, bkcode_namemap

def eastmoney_xbk_codeuniv_from_bkcf(
        xid='industry',
        bkcf_fname=datetime.today().strftime("%Y-%m-%d")+".csv",
        bkcodelist_fname='bkcodelist.yaml',
        bkcodenamemap_fname='bkcodenamemap.yaml'
    ):
    xurl=_furl_dict[f'bk_{xid}_cf']
    bkcf_saveroot=_save_root_dict[f'{xid}_bkcf_raw']

    xres = requests.get(xurl)
    bkcfpd = pd.DataFrame(json.loads(xres.text)['data']['diff'])
    bkcfpd.to_csv(bkcf_saveroot + bkcf_fname)

    bkcode_list = list(bkcfpd['f12'].unique())
    update_yaml(bkcf_saveroot + bkcodelist_fname, bkcode_list, unique=True)

    bkcode_namemap = dict(bkcfpd[['f12', 'f14']].values)
    update_yaml(bkcf_saveroot + bkcodenamemap_fname, bkcode_namemap, unique=True)
    return bkcfpd, bkcode_list, bkcode_namemap

# def eastmoney_each_xbk_info(
#         bkcode_list=[],
#         xid='industry',
#         bknamesdict_fname='bknamesdict.yaml',
#         codenamemap_fname='codenamemap.yaml',

#     ):
#     bknames_furl=_furl_dict['xbk_names']
#     bknames_saveroot=_save_root_dict[f'{xid}_bknames_raw']
#     bknames_dict = {}
#     code_namemap = {}
#     for bk in tqdm(bkcode_list[:]):
#         bknames_dict, code_namemap = bknames_url_processor(
#             bk,
#             bknames_furl,
#             bknames_dict,
#             code_namemap,
#             bknames_saveroot
#         )
#         update_yaml(bknames_saveroot+codenamemap_fname, code_namemap)
#     update_yaml(bknames_saveroot+bknamesdict_fname, bknames_dict)
#     update_yaml(bknames_saveroot+codenamemap_fname, code_namemap)
#     return bknames_dict, code_namemap

def bknames_url_processor(
        bk, 
        bknames_furl=_furl_dict['xbk_names'], 
        bknames_saveroot=_save_root_dict['industry_bknames_raw'],
        xid='industry'
        ):
    xurl = bknames_furl.format(np.random.randint(40), bk)
    if xid!='industry':
        xurl = xurl.replace(",f3,f62", "") # suppose save some time prevent screen duplicate info;/ unless later found concept contain names not been included in industry

    try:
        xres = requests.get(xurl)
    except Exception as e:
        print(e)
        _time.sleep(5)
        try:
            xres = requests.get(xurl)
        except:
            shared._bknames_url_processor_failed[xid].append(bk)
            return 

    xinfopd = pd.DataFrame(json.loads(xres.text)['data']['diff'])

    # unique names
    update_yaml(bknames_saveroot+"{}.yaml".format(bk), dict(xinfopd[['f12', 'f14']].values))

    # performance - only need to update industry one
    if xid=='industry':
        if datetime.today().strftime("%H:%M:%S") > '15:00:00':
            _curdt = datetime.today().strftime("%Y-%m-%d") + ' 15:00:00'
        elif datetime.today().strftime("%H:%M:%S") < '09:15:00':
            _curdt = datetime.today().strftime("%Y-%m-%d") + ' 09:14:59'
        elif np.all([
            datetime.today().strftime("%H:%M:%S") < '13:00:00',
            datetime.today().strftime("%H:%M:%S") > '11:30:00',
        ], axis=0):
            _curdt = datetime.today().strftime("%Y-%m-%d") + ' 11:30:00'
        else:
            _curdt = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        _dictlist = [{'date': _curdt, 'ticker': b, 'pctchg': c, 'zljlr': d} for b, c, d in xinfopd[['f12', 'f3', 'f62']].values]
        # update_yaml(bknames_saveroot.replace(xid, "")+"bknames_perf.yaml".format(bk), _dictlist)
        update_yaml(bknames_saveroot+"{}_perf.yaml".format(bk), _dictlist)

    shared._bknames_url_processor_success[xid].append(bk)
    return 

@_multitasking.task
def bknames_url_processor_multi(
        bk, 
        bknames_furl=_furl_dict['xbk_names'], 
        bknames_saveroot=_save_root_dict['industry_bknames_raw'],
        xid='industry',
    ):
    bknames_url_processor(
        bk, 
        bknames_furl=bknames_furl, 
        bknames_saveroot=bknames_saveroot,
        xid=xid
    )

def eastmoney_each_xbk_info_multi(
        bkcode_list=[],
        xid='industry',
    ):
    bknames_furl=_furl_dict['xbk_names']
    bknames_saveroot=_save_root_dict[f'{xid}_bknames_raw']
    shared._bknames_url_processor_success[xid]=[]
    shared._bknames_url_processor_failed[xid]=[]
    for bk in tqdm(bkcode_list[:]):
        bknames_url_processor_multi(
            bk,
            bknames_furl,
            bknames_saveroot,
            xid
        )

    _t = 0
    while len(shared._bknames_url_processor_failed[xid]) + len(shared._bknames_url_processor_success[xid]) < len(bkcode_list):
        _time.sleep(1)
        _t += 1
        if _t==100:
            break
        
    print("Finished... or Timeout...", str(len(shared._bknames_url_processor_failed[xid])), "Failed")
    if xid=='industry':
        _retrive_perfinfo_from_bkfolder(xid, _base=True)
    
    return 

def _retrive_perfinfo_from_bkfolder(xid, perfinfofname="bknames_perf.yaml", _base=False):
    xroot=_save_root_dict[f'{xid}_bknames_raw']
    fs = [x for x in os.listdir(xroot) if "_perf" in x]
    fs_info = reduce(lambda x,y: x+y, [read_yaml_file(xroot + f) for f in fs])
    if _base:
        update_yaml(xroot.replace(xid, "") + perfinfofname, fs_info)
    return fs_info

def _retrive_perfinfo_at_specific_date(_selected_dt='2024-07-05 15:00:00', fs_info=None, 
        fs_info_fpath=_savepath_fdict['bknames_perf_listdict'], _base=False):
    if fs_info is None:
        if _base:
            fs_info = _retrive_perfinfo_from_bkfolder("industry", _base=_base)
        else:
            try:
                fs_info = read_yaml_file(fs_info_fpath)
            except:
                fs_info = _retrive_perfinfo_from_bkfolder("industry", _base=_base)

    infopd = pd.DataFrame(fs_info)
    infopd['date'] = pd.to_datetime(infopd['date'], format="%Y-%m-%d %H:%M:%S")
    infopd = infopd.set_index('date')

    _sub_infopd = infopd.loc[_selected_dt]
    _sub_infodict = {}
    for i in range(len(_sub_infopd)):
        _xs = _sub_infopd.iloc[i]
        _sub_infodict[_xs['ticker']] = {
            'pctchg': _xs['pctchg'],
            'zljlr': _xs['zljlr']
        }
    return _sub_infodict


def query_period_cf_allstock(periodcode='f62', pageSize=6000, pageNumber=1, curdate='', savepath=icloud_froot+"/env/data/capital_flow/"):
    """
        Get period capitalflow info.

        curdate: filename
    """
    _urlbase = "https://push2.eastmoney.com/api/qt/clist/get?"
    _params = {
        "cb": "", #"jQuery112306955742794869183_1730816130885",
        "fid": periodcode, # 今日排行 f62；3日排行 f267；5日排行 f164；10日排行 f174；
        "po": "1",
        "pz": pageSize,
        "pn": pageNumber,
        "np": "1", # affect direction of the table
        "fltt": "2",
        "invt": "2",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "fs": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
        "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
    }

    xres = requests.get(_urlbase, params=_params)
    if _params["cb"]=="":
        info = xres.text.replace(_params['cb'], "")[:]
    else:
        info = xres.text.replace(_params['cb'], "")[1:-2]
    infopd = pd.DataFrame(json.loads(info)['data']['diff'])
    # selectedpd = infopd[['f12', 'f3', 'f62', 'f66', 'f72', 'f78', 'f84']]
    selectedpd = infopd[['f12', 'f3', 'f62', 'f184', 'f66', 'f72', 'f78', 'f84']]
    if savepath is not None:
        selectedpd.to_csv(os.path.join(savepath, f"{curdate}.csv"))
    return selectedpd


def query_period_cf_allstock_10d(periodcode='f12', pageSize=6000, pageNumber=1, curdate='', savepath=icloud_froot+"/env/data/capital_flow_10d/"):
    """
        Get period capitalflow info.

        curdate: filename
    """
    _urlbase = "https://push2.eastmoney.com/api/qt/clist/get?"
    _params = {
        "cb": "", #"jQuery112306955742794869183_1730816130885",
        "fid": periodcode, 
        "po": "1",
        "pz": pageSize,
        "pn": pageNumber,
        "np": "1", # affect direction of the table
        "fltt": "2",
        "invt": "2",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "fs": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
        "fields": "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124,f1,f13",
    }

    xres = requests.get(_urlbase, params=_params)
    if _params["cb"]=="":
        info = xres.text.replace(_params['cb'], "")[:]
    else:
        info = xres.text.replace(_params['cb'], "")[1:-2]
    infopd = pd.DataFrame(json.loads(info)['data']['diff'])
    # selectedpd = infopd[['f12', 'f3', 'f62', 'f66', 'f72', 'f78', 'f84']]
    selectedpd = infopd[['f12', 'f160', 'f174', 'f175', 'f176', 'f178', 'f180', 'f182']]
    if savepath is not None:
        selectedpd.to_csv(os.path.join(savepath, f"{curdate}.csv"))
    return selectedpd


def query_period_cf_allstock_3d(periodcode='f268', pageSize=6000, pageNumber=1, curdate='', savepath=icloud_froot+"/env/data/capital_flow_3d/"):
    """
        Get period capitalflow info.

        curdate: filename
    """
    _urlbase = "https://push2.eastmoney.com/api/qt/clist/get?"
    _params = {
        "cb": "", #"jQuery112306955742794869183_1730816130885",
        "fid": periodcode, 
        "po": "1",
        "pz": pageSize,
        "pn": pageNumber,
        "np": "1", # affect direction of the table
        "fltt": "2",
        "invt": "2",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "fs": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
        "fields": "f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124,f1,f13",
    }

    xres = requests.get(_urlbase, params=_params)
    if _params["cb"]=="":
        info = xres.text.replace(_params['cb'], "")[:]
    else:
        info = xres.text.replace(_params['cb'], "")[1:-2]
    infopd = pd.DataFrame(json.loads(info)['data']['diff'])
    # selectedpd = infopd[['f12', 'f3', 'f62', 'f66', 'f72', 'f78', 'f84']]
    selectedpd = infopd[['f12', 'f127', 'f267', 'f268', 'f269', 'f270', 'f272', 'f274']]
    if savepath is not None:
        os.makedirs(savepath, exist_ok=True)
        selectedpd.to_csv(os.path.join(savepath, f"{curdate}.csv"))
    return selectedpd



def query_period_cf_allstock_5d(periodcode='f165', pageSize=6000, pageNumber=1, curdate='', savepath=icloud_froot+"/env/data/capital_flow_5d/"):
    """
        Get period capitalflow info.

        curdate: filename
    """
    _urlbase = "https://push2.eastmoney.com/api/qt/clist/get?"
    _params = {
        "cb": "", #"jQuery112306955742794869183_1730816130885",
        "fid": periodcode, 
        "po": "1",
        "pz": pageSize,
        "pn": pageNumber,
        "np": "1", # affect direction of the table
        "fltt": "2",
        "invt": "2",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "fs": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
        "fields": "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124,f1,f13",
    }

    xres = requests.get(_urlbase, params=_params)
    if _params["cb"]=="":
        info = xres.text.replace(_params['cb'], "")[:]
    else:
        info = xres.text.replace(_params['cb'], "")[1:-2]
    infopd = pd.DataFrame(json.loads(info)['data']['diff'])
    # selectedpd = infopd[['f12', 'f3', 'f62', 'f66', 'f72', 'f78', 'f84']]
    selectedpd = infopd[['f12', 'f109', 'f164', 'f165', 'f166', 'f168', 'f170', 'f172']]
    if savepath is not None:
        os.makedirs(savepath, exist_ok=True)
        selectedpd.to_csv(os.path.join(savepath, f"{curdate}.csv"))
    return selectedpd

def query_period_cf_allstock_rtn(periodcode='f62', pageSize=6000, pageNumber=1, curdate='', savepath=icloud_froot+"/env/data/capital_flow/"):
    """
        Get period capitalflow info.

        curdate: filename
    """
    _urlbase = "https://push2.eastmoney.com/api/qt/clist/get?"
    _params = {
        "cb": "", #"jQuery112306955742794869183_1730816130885",
        "fid": periodcode, # 今日排行 f62；3日排行 f267；5日排行 f164；10日排行 f174；
        "po": "1",
        "pz": pageSize,
        "pn": pageNumber,
        "np": "1", # affect direction of the table
        "fltt": "2",
        "invt": "2",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "fs": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
        "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
    }

    xres = requests.get(_urlbase, params=_params)
    if _params["cb"]=="":
        info = xres.text.replace(_params['cb'], "")[:]
    else:
        info = xres.text.replace(_params['cb'], "")[1:-2]
    infopd = pd.DataFrame(json.loads(info)['data']['diff'])
    # selectedpd = infopd[['f12', 'f3', 'f62', 'f66', 'f72', 'f78', 'f84']]
    selectedpd = infopd.copy(deep=True) #[['f12', 'f3', 'f62', 'f184', 'f66', 'f72', 'f78', 'f84']]
    if savepath is not None:
        selectedpd.to_csv(os.path.join(savepath, f"{curdate}.csv"))
    return selectedpd


def eastmoney_query_index_constituents(
    indexcode=1, 
    savepath=icloud_froot + 'share/', 
    indexcodemap={
        1: 'hushen300', #沪深300
        2: 'shangzhen50', #上证50
        3: 'zhongzhen500', #中证
        4: 'kechuang50', #科创
        5: 'zhongzhenA50', #中证
        6: 'zhongzhenA500',
        7: 'zhongzhen1000',
        8: 'shenzheng50', #深证
        9: 'zhongxiao100', #中小
        10: 'beizhen50', #北证
        11: 'shangzhen180', #上证
        12: 'zhongzhenA100', #中证
        13: 'zhongzhen2000',
    }
):
    # "https://data.eastmoney.com/other/index/"
    import json
    import requests
    import pandas as pd
    
    def _get_single_page(pageNumber):
        _urlbase = "https://datacenter-web.eastmoney.com/api/data/v1/get?"
        _params = {
            "callback": "", #"jQuery1123038950198671999325_1747730881740",
            "sortColumns": 'SECURITY_CODE', 
            "sortTypes": "-1",
            "pageSize": 50,
            "pageNumber": pageNumber,
            'reportName': 'RPT_INDEX_TS_COMPONENT',
            'columns': 'SECUCODE,SECURITY_CODE,TYPE,SECURITY_NAME_ABBR,CLOSE_PRICE,INDUSTRY,REGION,WEIGHT,EPS,BPS,ROE,TOTAL_SHARES,FREE_SHARES,FREE_CAP',
            'quoteColumns': 'f2,f3',
            'quoteType': '0',
            'source': 'WEB',
            'client': 'WEB',
            'filter': f'(TYPE="{indexcode}")'
        }

        xres = requests.get(_urlbase, params=_params)
        return xres
    
    xlist = []
    pageNumber=1
    xres = _get_single_page(pageNumber)
    xlist.extend(json.loads(xres.text)['result']['data'])
    _total_pn = json.loads(xres.text)['result']['pages']
    print("_total_pn", _total_pn)
    while pageNumber < _total_pn:
        pageNumber += 1
        print(pageNumber, end=";")
        xres = _get_single_page(pageNumber)
        xlist.extend(json.loads(xres.text)['result']['data'])
        
    xpd = pd.DataFrame(xlist).drop_duplicates()
    if savepath is not None:
        import os
        os.makedirs(savepath, exist_ok=True)
        
        xpd.to_csv(os.path.join(savepath, f"index_constituents_{indexcodemap[indexcode]}.csv"))
    return xpd

def eastmoney_query_ST_names(
        savepath=env_db_root, 
        ):
    """
    
    zc: z-main board 00,60.., c-startup 30.., zc-both
    """

    # "https://data.eastmoney.com/bkzj/BK0511.html"
    import json
    import requests
    import pandas as pd

    def _get_single_page(pageNumber):
        _urlbase = "https://push2.eastmoney.com/api/qt/clist/get?"
        _params = {
            "callback": "", #"jQuery112301540295289230208_1749541441581",
            "fid": 'f3', 
            "po": 1,
            "pz": 50,
            "pn": pageNumber,
            'fltt': 2,
            'invt': 2,
            'ut': '8dec03ba335b81bf4ebdf7b29ec27d15',
            'fs': 'b:BK0511',
            'fields': "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
        }

        xres = requests.get(_urlbase, params=_params)
        return xres

    xlist = []
    pageNumber=1
    xres = _get_single_page(pageNumber)

    def _get_data(xres):
        return [v['f12'] for k, v in json.loads(xres.text)['data']['diff'].items()] 
    xlist.extend(_get_data(xres))
    total_ns = json.loads(xres.text)['data']['total']
    xlist = list(set(xlist))
    while len(xlist) < total_ns:
        pageNumber += 1
        print(pageNumber, end=";")
        xres = _get_single_page(pageNumber)
        xlist.extend(_get_data(xres))
        xlist = list(set(xlist))
        # print(pageNumber, _get_data(xres))

    xlist = sorted(xlist)
    # xpd = pd.DataFrame(xlist).drop_duplicates()
    if savepath is not None:
        import os
        os.makedirs(savepath, exist_ok=True)
        
        # xpd.to_csv(os.path.join(savepath, f"st_names.csv"))
        save_as_yaml(os.path.join(savepath, f"st_names.yaml"), xlist)
    return xlist

# def 
def get_stock_meta_data(
        a_univ_list, 
        dbroot = env_raw_root,
        save_dbroot = env_db_root
        ):
    tgt_flds = ['geo', 'industry', 'concept']
    stock_meta_dict = {k:{
        'name':'',
        'industry':[], # belongs to which industry bankuai
        'geo':[],
        'concept':[],
    } for k in a_univ_list}
    stock_codechinesemap = {k:'' for k in a_univ_list}
    for f in tgt_flds[:]:
        bkfs = [f for f in os.listdir(dbroot + f) if '_perf' not in f]
        for bkf in bkfs:
            bks_constituents = read_yaml_file(os.path.join(dbroot + f, bkf))
            _bk = bkf.replace(".yaml", "")
            stock_codechinesemap.update(bks_constituents)
            for k, v in bks_constituents.items():
                try:
                    stock_meta_dict[k][f].append(_bk)
                    stock_meta_dict[k]['name'] = v
                except KeyError:
                    try:
                        stock_meta_dict[k] = {
                                'name':v,
                                'industry':[], # belongs to which industry bankuai
                                'geo':[],
                                'concept':[],
                        }
                        stock_meta_dict[k][f].append(_bk)
                    except Exception as e:
                        print(e)
                        
    # push out no content tickers
    for k, vdict in stock_meta_dict.items():
        _str = ""
        for kk, vv in vdict.items():
            if len(vv)==0:
                if kk=='name':
                    CCSTART = '\033[91m'
                    CCEND = '\033[0m'
                    _str += " {} {} {}".format(CCSTART, kk, CCEND)
                elif kk=='industry':
                    CCSTART = '\033[92m'
                    CCEND = '\033[0m'
                    _str += " {} {} {}".format(CCSTART, kk, CCEND)
                elif kk=='concept':
                    CCSTART = '\033[94m'
                    CCEND = '\033[0m'
                    _str += " {} {} {}".format(CCSTART, kk, CCEND)
                elif kk=='geo':
                    CCSTART = '\033[95m'
                    CCEND = '\033[0m'
                    _str += " {} {} {}".format(CCSTART, kk, CCEND)
            if len(_str)>0:
                print(k, _str, 'is Empty')

    save_as_yaml(save_dbroot+'stock_meta_dict.yaml', stock_meta_dict)
    save_as_yaml(save_dbroot+'stock_codechinesemap.yaml', stock_codechinesemap)

    bk_namemap = {}
    for f in tgt_flds:
        xdict = read_yaml_file(dbroot+"bkcf/"+f+"/bkcodenamemap.yaml")
        bk_namemap.update(xdict)
    save_as_yaml(save_dbroot+'bk_namemap.yaml', bk_namemap)
    return
