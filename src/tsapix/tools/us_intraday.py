import pandas as pd
import numpy as np
from datetime import datetime
import time
from tqdm import tqdm

import os
# icloud_froot = "/Users/{}/Library/Mobile Documents/com~apple~CloudDocs/".format(os.environ['USER'])
from tsapi.utils import icloud_froot

import talib

# def _color_txt(xstr):
#     return '\033[91m'+xstr+'\033[0m'

# def _black_txt(xstr):
#     return '\033[30m'+xstr+'\033[0m'

######### FORMATTING
def print_infotbl(timestr=['', ''], con1=['', ''], nbys=['', ''], nbysprob=['', ''], _space=20, n=4, rs=2):
    print('- '*int(n*_space/2 + n-1))
    xstr1 = '\033[30m'+'NBProb'+'\033[0m'
    xstr2 = '\033[30m'+'NB'+'\033[0m'
    xstr3 = '\033[30m'+'con1'+'\033[0m'
    print(f"{'Time': ^{_space}}|{xstr1 : ^{_space}}|{xstr2 : ^{_space}}|{xstr3 : ^{_space}}")
    print('- '*int(n*_space/2 + n-1))
    for i in range(rs):
        print(f"{timestr[i] : ^{_space}}|{nbysprob[i] : ^{_space}}|{nbys[i] : ^{_space}}|{con1[i] : ^{_space}}")
        print('- '*int(n*_space/2 + n-1))
#     print('Time'.ljust(_space), '|', 'status_1'.ljust(_space), '|', 'status_0'.ljust(_space), '|')
    return
#########

def add_macd_elements_topd(xpd, pxcol='Adj Close'):
    xpd = xpd.copy(deep=True)
    prefix = '' if pxcol in ['Adj Close', 'Close'] else pxcol + "_"
    xpd[f'{prefix}macd'], xpd[f'{prefix}macd_signal'], xpd[f'{prefix}macd_hist'] = talib.MACD(xpd[pxcol], fastperiod=12, slowperiod=26, signalperiod=9)
    return xpd

def add_macd_elements_topd_paras(xpd, pxcol='Adj Close', fastperiod=12, slowperiod=26, signalperiod=9):
    _suffix = f"_{fastperiod}_{slowperiod}_{signalperiod}"
    xpd = xpd.copy(deep=True)
    prefix = '' if pxcol in ['Adj Close', 'Close'] else pxcol + "_"
    xpd[f'{prefix}macd{_suffix}'], \
        xpd[f'{prefix}macd_signal{_suffix}'], \
            xpd[f'{prefix}macd_hist{_suffix}'] = talib.MACD(xpd[pxcol], 
                fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    return xpd

def add_kdj_elements_topd(xpd, hcol='High', lcol='Low', ccol='Close', prefix=None):
    xpd = xpd.copy(deep=True)
    if prefix is None:
        prefix = '' if ccol in ['Adj Close', 'Close'] else ccol + "_"
    xpd[f'{prefix}k'], xpd[f'{prefix}d'] = talib.STOCH(
        xpd[hcol],
        xpd[lcol],
        xpd[ccol],
        fastk_period=9,
        slowk_period=3,
        slowk_matype=0,
        slowd_period=3,
        slowd_matype=0
    )
    xpd[f'{prefix}j'] = 3 * xpd[f'{prefix}k'] - 2 * xpd[f'{prefix}d']
    return xpd

def add_kdj_elements_topd_paras(xpd, hcol='High', lcol='Low', ccol='Close', prefix=None, 
                                fastk_period=9, slowk_period=3, slowd_period=3):
    _suffix = f"_{fastk_period}_{slowk_period}_{slowd_period}"
    xpd = xpd.copy(deep=True)
    if prefix is None:
        prefix = '' if ccol in ['Adj Close', 'Close'] else ccol + "_"
    _k, _d, _j = f'{prefix}k{_suffix}', f'{prefix}d{_suffix}', f'{prefix}j{_suffix}'
    xpd[_k], xpd[_d] = talib.STOCH(
        xpd[hcol],
        xpd[lcol],
        xpd[ccol],
        fastk_period=9,
        slowk_period=3,
        slowk_matype=0,
        slowd_period=3,
        slowd_matype=0
    )
    xpd[_j] = 3 * xpd[_k] - 2 * xpd[_d]
    return xpd

def add_rolling_rank(xpd, xcols=['macd', 'j'], rws=[30, 60], scale=True):
    xpd = xpd.copy(deep=True)
    for rw in rws:
        for c in tqdm(xcols):
            _colname = f"{c}_rel{rw}"
            xpd[_colname] = xpd[c].rolling(rw).apply(lambda x: np.argsort(np.argsort(x)).values[-1])
            if scale:
                xpd[_colname] = xpd[_colname] / (rw - 1)
    return xpd
    
def print_trading_bar():
    from datetime import datetime, timedelta
    
    us_now = datetime.now() - timedelta(minutes=13*60)
    trade_date = us_now.strftime("%Y-%m-%d")
    trade_starttime = trade_date + " 09:30"
    trade_starttime = datetime.strptime(trade_starttime, "%Y-%m-%d %H:%M")
    trade_endtime = trade_date + " 16:00"
    trade_endtime = datetime.strptime(trade_endtime, "%Y-%m-%d %H:%M")
    
    total_secs = (trade_endtime - trade_starttime).seconds
    gone_secs =(us_now - trade_starttime).seconds
    
    print("Trading Bar: {:.2f}% ({}/{} secs)".format(
        100 * (gone_secs / total_secs),
        gone_secs,
        total_secs
    ))

#############################################################
# trading interface WEBULL
import pyautogui

positions_dict = {
    'symbol': (276, 375),
    'side': {
        'buy': (460, 187),
        'sell': (585, 190),
    },
    'placeorder_market': (474, 353),
    'placeorder_limit': (512, 416),
    'num': (559, 251),

}

positions_dict_options = {
    'symbol': (276, 375),
    'side': {
        'buy': (460, 253),
        'sell': (585, 249),
    },
    'placeorder_market': (569, 478),
#     'placeorder_limit': (543, 542),
    'num': (550, 313),

}

_order_gap = 5


def place_market_order(side='buy', num=1, instrument='equity'):
    if instrument=='equity':
        xydict = positions_dict.copy()
    elif instrument=='options':
        xydict = positions_dict_options.copy()
#     pyautogui.click(xydict['symbol'])
    pyautogui.click(xydict['side'][side])
    if num>1:
        modify_shares_num(num=num, positions_dict=xydict)
    pyautogui.click(xydict['placeorder_market'])
    # pyautogui.click(xydict['placeorder_limit']) #### delete
    _order_timstr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(side.upper(), 'market order placed at ', _order_timstr, "(Instrument: ", instrument, ")")
    return {
        '_order_timstr': _order_timstr,
        'side': side,
    }

def modify_shares_num(num=1, positions_dict=positions_dict):
    pyautogui.click(positions_dict['num'])
    pyautogui.press('backspace')
    pyautogui.write(str(num))
    pyautogui.press('enter')


def live():
    return {
        '_data_timstr': 0,
        'status_1': False,
        'status_0': False,
    }

class LiveTrader:

    def __init__(self, 
                 indfunc=live, 
                 trading_indstr='status_0',
                 inipos=0,
                 instrument='equity',
                ):
        self.position = inipos
        self.order_records = {}
        self.indfunc = indfunc
        self.trading_indstr = trading_indstr
        self.instrument = instrument

        self.metrics = {
            'buy': 0,
            'sell': 0,
        } # record some metrics

        self.cur_date = datetime.now().strftime("%Y-%m-%d")
        self.order_records_savedir = icloud_froot + 'env/projects/tsla_1yr/trading_log/'
        self.order_records_savepath = f"{self.order_records_savedir}/{self.cur_date}.csv"

    def log_records(self):
        try:
            pd.DataFrame(self.order_records).T.to_csv(self.order_records_savepath)
        except Exception as e:
            print('Order Log Failed, ', e)

    def log_trading_metrics(self):
        try:
            print('Trade times: ', 'buy', self.metrics['buy'], '; sell', self.metrics['sell'], '; sum', self.metrics['buy'] + self.metrics['sell'])
        except Exception as e:
            print('Metrics Log Failed, ', e)

    def pure_long_trading(self):
        try:
            xdict = self.indfunc()
        except Exception as e:
            print("Error updating... ", e)
            return

        trading_indstr = self.trading_indstr
        # trading_indstr = 'random'
        print(trading_indstr)

        if trading_indstr == 'random':
            xdict[trading_indstr] = np.random.random() > 0.5

        # # place buy order
        print(xdict[trading_indstr], self.position, xdict[trading_indstr]==False, str(xdict[trading_indstr])=='False', int(xdict[trading_indstr])==0)
        if np.all([
            str(xdict[trading_indstr])=='False' or int(xdict[trading_indstr])==0,
            self.position==0
        ]): 
            _odt = place_market_order(side='buy')
            self.position+=1
            self.order_records[_odt['_order_timstr']] = {
                'side': _odt['side'],
                'pos': self.position,
            }
            self.metrics['buy'] += 1

        # # place sell order
        if np.all([
            str(xdict[trading_indstr])=='True' or int(xdict[trading_indstr])==1,
            self.position>0
        ]):
            while self.position>0:
                _odt = place_market_order(side='sell')
                self.position-=1
                self.order_records[_odt['_order_timstr']] = {
                    'side': _odt['side'],
                    'pos': self.position,
                }

                self.metrics['sell'] += 1

        print("Current Position: ", self.position)
        self.log_records()
        self.log_trading_metrics()

    def long_short_trading(self, ):
        try:
            xdict = self.indfunc()
        except Exception as e:
            print("Error updating... ", e)
            return

        trading_indstr = self.trading_indstr
        # trading_indstr = 'random'
        print(trading_indstr)

        if trading_indstr == 'random':
            xdict[trading_indstr] = np.random.random() > 0.5

        # # place buy order
        print(xdict[trading_indstr], self.position, xdict[trading_indstr]==False, str(xdict[trading_indstr])=='False', int(xdict[trading_indstr])==0)
        if np.all([
            str(xdict[trading_indstr])=='False' or int(xdict[trading_indstr])==0,
            self.position==0
        ]): 
            _odt = place_market_order(side='buy', instrument=self.instrument)
            self.position+=1
            self.order_records[_odt['_order_timstr']] = {
                'side': _odt['side'],
                'pos': self.position,
            }
            self.metrics['buy'] += 1

        if np.all([
            str(xdict[trading_indstr])=='False' or int(xdict[trading_indstr])==0,
            self.position==-1
        ]): 
            for i in range(2):
                _odt = place_market_order(side='buy', num=1, instrument=self.instrument)
                self.position+=1
                self.order_records[_odt['_order_timstr']] = {
                    'side': _odt['side'],
                    'pos': self.position,
                }
                self.metrics['buy'] += 1
                time.sleep(_order_gap) # in case order not filled

        # # place sell order
        if np.all([
            str(xdict[trading_indstr])=='True' or int(xdict[trading_indstr])==1,
            self.position==0
        ]):
            _odt = place_market_order(side='sell', instrument=self.instrument)
            self.position-=1
            self.order_records[_odt['_order_timstr']] = {
                'side': _odt['side'],
                'pos': self.position,
            }

            self.metrics['sell'] += 1

        if np.all([
            str(xdict[trading_indstr])=='True' or int(xdict[trading_indstr])==1,
            self.position==1
        ]):
            for i in range(2):
                _odt = place_market_order(side='sell', num=1, instrument=self.instrument)
                self.position-=1
                self.order_records[_odt['_order_timstr']] = {
                    'side': _odt['side'],
                    'pos': self.position,
                }

                self.metrics['sell'] += 1
                time.sleep(_order_gap)

        

        print("Current Position: ", self.position)
        self.log_records()
        self.log_trading_metrics()

    def pure_short_trading(self):
        try:
            xdict = self.indfunc()
        except Exception as e:
            print("Error updating... ", e)
            return

        trading_indstr = self.trading_indstr
        # trading_indstr = 'random'
        print(trading_indstr)

        if trading_indstr == 'random':
            xdict[trading_indstr] = np.random.random() > 0.5

        # # place buy order
        print(xdict[trading_indstr], self.position, xdict[trading_indstr]==False, str(xdict[trading_indstr])=='False')
        if np.all([
            str(xdict[trading_indstr])=='False' or int(xdict[trading_indstr])==0,
            self.position==-1
        ]): 
            _odt = place_market_order(side='buy', instrument=self.instrument)
            self.position+=1
            self.order_records[_odt['_order_timstr']] = {
                'side': _odt['side'],
                'pos': self.position,
            }
            self.metrics['buy'] += 1

        # # place sell order
        if np.all([
            str(xdict[trading_indstr])=='True' or int(xdict[trading_indstr])==1,
            self.position==0
        ]):
            _odt = place_market_order(side='sell', instrument=self.instrument)
            self.position-=1
            self.order_records[_odt['_order_timstr']] = {
                'side': _odt['side'],
                'pos': self.position,
            }

            self.metrics['sell'] += 1

        print("Current Position: ", self.position)
        self.log_records()
        self.log_trading_metrics()
        return
    
    def pure_short_trading_puts(self):
        try:
            xdict = self.indfunc()
        except Exception as e:
            print("Error updating... ", e)
            return

        trading_indstr = self.trading_indstr
        # trading_indstr = 'random'
        print(trading_indstr)

        if trading_indstr == 'random':
            xdict[trading_indstr] = np.random.random() > 0.5

        # # place sell order
        print(xdict[trading_indstr], self.position, xdict[trading_indstr]==False, str(xdict[trading_indstr])=='False')
        if np.all([
            str(xdict[trading_indstr])=='False' or int(xdict[trading_indstr])==0,
            self.position==1
        ]): 
            _odt = place_market_order(side='sell', instrument=self.instrument)
            self.position-=1
            self.order_records[_odt['_order_timstr']] = {
                'side': _odt['side'],
                'pos': self.position,
            }
            self.metrics['sell'] += 1

        # # place buy order
        if np.all([
            str(xdict[trading_indstr])=='True' or int(xdict[trading_indstr])==1,
            self.position==0
        ]):
            _odt = place_market_order(side='buy', instrument=self.instrument)
            self.position+=1
            self.order_records[_odt['_order_timstr']] = {
                'side': _odt['side'],
                'pos': self.position,
            }

            self.metrics['buy'] += 1

        print("Current Position: ", self.position)
        self.log_records()
        self.log_trading_metrics()
        return

