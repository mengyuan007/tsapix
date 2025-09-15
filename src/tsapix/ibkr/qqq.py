from ibapi.client import *
from ibapi.wrapper import *
import datetime
import time
import threading

port = 7496


class DataApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.orderId=0
        self.datapool = {}

    def nextValidId(self, orderId: OrderId):
        self.orderId = orderId
    
    def nextId(self):
        self.orderId += 1
        return self.orderId
    
    def error(self, reqId, errorCode, errorString, advancedOrderReject=""):
        print(f"reqId: {reqId}, errorCode: {errorCode}, errorString: {errorString}, orderReject: {advancedOrderReject}")
    
    def historicalData(self, reqId, bar):
        print(reqId, bar)
        if reqId not in self.datapool.keys():
            self.datapool[reqId] = []
        self.datapool[reqId].append(bar)
    
    def historicalDataEnd(self, reqId, start, end):
        print(f"Historical Data Ended for {reqId}. Started at {start}, ending at {end}")
        self.cancelHistoricalData(reqId)

# app = DataApp()
# app.connect("127.0.0.1", port, 0)
# threading.Thread(target=app.run).start()
# time.sleep(1)


def init_qqq():
    contractbase = Contract()
    contractbase.symbol = "QQQ"
    contractbase.secType = "STK"
    contractbase.exchange = "SMART"
    contractbase.currency = "USD"
    return contractbase

# contractx = init_qqq()


def init_qqq_options(ltd='20250527', rt='P', stk=510):
    contract1 = Contract()
    contract1.symbol = "QQQ"
    contract1.secType = "OPT"
    contract1.exchange = "SMART"
    contract1.currency = "USD"
    contract1.lastTradeDateOrContractMonth = ltd
    contract1.right = rt
    contract1.strike = stk
    return contract1

def init_tsla_options(ltd='20250527', rt='P', stk=510):
    contract1 = Contract()
    contract1.symbol = "TSLA"
    contract1.secType = "OPT"
    contract1.exchange = "SMART"
    contract1.currency = "USD"
    contract1.lastTradeDateOrContractMonth = ltd
    contract1.right = rt
    contract1.strike = stk
    return contract1


# import yfinance as yf

# qqqpx = yf.download('QQQ')
# qqqpxpd = qqqpx.xs('QQQ', axis=1, level=1)



def get_qqq_bardatapd(rawdatalist, _reqid, suffix=None, savepath=None, paramslog={}):
    import re
    import pandas as pd
    import os
    barsdata = re.findall(
    "([0-9]{2}[:][0-9]{2}[:][0-9]{2}) US/Eastern, Open: ([.0-9]+), High: ([.0-9]+), Low: ([.0-9]+), Close: ([.0-9]+), Volume: ([.0-9]+)", 
    " ".join([str(x) for x in rawdatalist]))
    _rt, _ltd, _bst, _ltddate, _stk = paramslog[_reqid]
    frq = _bst[1].replace(" ", "")
    fpath = f'{savepath}/{_ltddate}/'
    os.makedirs(fpath, exist_ok=True)
    if suffix is None:
        pd.DataFrame(barsdata).to_csv(f'{fpath}/0DTE{_rt}{_stk}_{frq}.csv')
    else:
        pd.DataFrame(barsdata).to_csv(f'{fpath}/0DTE{_rt}{_stk}_{frq}.csv')



# rtlist = ['C', 'P']
# ltdlist = [f"{xdt} 16:00:00 US/Eastern" for xdt in [
#     (datetime.datetime.today() - datetime.timedelta(x)).strftime("%Y%m%d") for x in range(1, 2)
# ]]
# barsetting = [("1 D", "1 min", "TRADES")]
# # barsetting = [("1 D", "5 mins", "TRADES")]

# from itertools import product

# _reqlist = list(product(rtlist, ltdlist, barsetting))

# paramslog = {}

# from tqdm import tqdm

# for _req in tqdm(_reqlist):
#     _rt, _ltd, _bst = _req
#     _ltddate = _ltd.split(" ")[0]
#     stkrange = range(int(qqqpxpd.loc[_ltddate]['Low'])-20, int(qqqpxpd.loc[_ltddate]['High'])+20)
#     for _stk in stkrange:
#         _contract = init_qqq_options(_ltddate, _rt, _stk)
        
#         _reqid = app.nextId()
#         paramslog[_reqid] = [_rt, _ltd, _bst, _ltddate, _stk]
#         print("Processing", _reqid, paramslog[_reqid])
#         app.reqHistoricalData(
#             _reqid, 
#             _contract, 
#             _ltd, 
#             _bst[0], 
#             _bst[1], 
#             _bst[2], 
#             1, 
#             1, 
#             False, 
#             [])
        
#         try:
#             get_qqq_bardatapd(app.datapool[_reqid], _reqid)
#         except:
#             print("extract datapd failed", _reqid)
        
#         if _reqid%10==0:
#             time.sleep(10)


# time.sleep(60)

# strdatapool = {}
# for k, v in app.datapool.items():
#     strdatapool[k] = [str(x) for x in v]

# for k, v in strdatapool.items():
#     _suffix = "{}{}{}_{}".format(paramslog[k][3], paramslog[k][0], paramslog[k][4], paramslog[k][2][1])
#     get_qqq_bardatapd(v, k, _suffix, 
#                       savepath="/Users/my/Library/Mobile Documents/com~apple~CloudDocs/env/projects/us_intraday/QQQ/options/", paramslog=paramslog)

    