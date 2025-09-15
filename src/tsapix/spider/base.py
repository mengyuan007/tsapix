from .utils import *

try:
    a_code_univlist = read_yaml_file(code_univ_save_path)
except:
    a_code_univlist = []
sz_identifier_0 = ['0', '3'] # listed in Shen Zhen if ticker start with 0 or 3


histpx_cols = ['Open', 'Close', 'High', 'Low', 'TradeShares', 'TradeAmt', 'ZF', 'AbsChg', 'PctChg', 'TurnoverRate']
histcf_cols = ['zljlr_je','xdjlr_je','zdjlr_je','ddjlr_je','cddjlr_je','zljlr_jzb','xdjlr_jzb','zdjlr_jzb','ddjlr_jzb','cddjlr_jzb','Close','PctChg','nan1','nan2']

china_tcalendar = mcal.get_calendar('SSE')

def _continuous_auction_period(x):
    return np.any([
            np.all([x.strftime("%H:%M:%S")<="15:00:00", x.strftime("%H:%M:%S")>="13:00:00"], axis=0),
            np.all([x.strftime("%H:%M:%S")<="11:30:00", x.strftime("%H:%M:%S")>="09:30:00"], axis=0),
        ], axis=0)

def _call_auction_period(x):
    return np.all([x.strftime("%H:%M:%S")>="09:15:00", x.strftime("%H:%M:%S")<="09:25:00"], axis=0)

def _sv(xobj, a0=0,): # slicing view
    return pd.DataFrame(xobj.xcube[a0, :, :], index=xobj.axsesinfo[1], columns=xobj.axsesinfo[2])

_eastmoney_filed_meaningdict = {
    
}


def get_stock_meta_dict():
    """ Dict record stock meta info:

    Element Structure
    '000001': {
        'name': 'xxx',
        'industry': [],
        'geo': [],
        'concept: [],
    }
    
    """
    return read_yaml_file(env_db_root + "stock_meta_dict.yaml")

def get_stock_codechinesemap():
    """ Dict record stock code&name info:

    Element Structure
    '000001': 'xxx'
    
    """
    return read_yaml_file(env_db_root + "stock_codechinesemap.yaml")

def get_bk_namemap():
    """ Dict record bankuai(sector) code&name info:

    Element Structure
    'BKXXX': 'xxx'
    
    """
    return read_yaml_file(env_db_root + "bk_namemap.yaml")

def load_maps():
    xdict = {
        'stock_meta': get_stock_meta_dict(),
        'bkname': get_bk_namemap(),
    }
    print("Maps Available Keys: ", list(xdict.keys()))
    return xdict

def load_cube_n_axes(pairname=None, froot=None, timeformat="%Y-%m-%d %H:%M"):
    xcube = read_npcube(f"{froot}/{pairname}.npz")
    xaxes = read_yaml_file(f"{froot}/{pairname}.yaml")
    xaxes[1] = pd.to_datetime(xaxes['1str'], format=timeformat)
    return {
        'cube': xcube,
        'axes': xaxes,
    }

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
