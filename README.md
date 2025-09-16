# TSApiX
## :snake: Create environment for Quants / Agents to play.

After installation and some setup, you will get an Environment to test your ideas, to test strategies, and to play. Have Fun!
<br><br>

### :clock12: Installation

#### 1. Install Package 
>[!NOTE]
>Assume Python environment already established in your working space. If not, please install Python environment first.
```
pip install tsapix
```
#### 2. Personalise DataBase Location
Database is a key element for quant environment. 
TSApiX come with a default database location, it can be personalised in [tsapix/utils.py](https://github.com/mengyuan007/tsapix/blob/main/src/tsapix/utils.py)
at Line 8. Simply assign your target location to the parameter :jigsaw:```icloud_froot```

#### 3. Initiate Environment
- Open Terminal
- Type ```python -m site --user-site ```, press ```Enter``` to get Python site-pakages location
- Type ```cd [Python site-pakages location]```, press ```Enter```
- Type ```cd tsapix```, press ```Enter```
- Type ```python setup.py```, press ```Enter```

#### 4. Personalise Environment Data
As the component of Environment shall be flexible, you can decide which data to be ingested in your environment. Detailed illustration can be found in the following sections.

###  :clock1: Personalise Environment Data
#### 1. China Market - Price
:jigsaw:```HistPX``` is the primary Class realise data ingestion.
<br><br>
A sample of data ingestion can be found [here](https://github.com/mengyuan007/tsapix/blob/main/_sample/spider_update_database_China.ipynb).

Depending on your target trading strategy, you may only download data suit your time frames.
Supported time frequency and price type settings are the **keys** of dictionary :jigsaw: ```kltmapdict``` and :jigsaw: ```fqtmapdict``` in [this file](https://github.com/mengyuan007/tsapix/blob/main/src/tsapix/spider/eastmoney.py).

##### Example
```
from tsapix.utils import *
import tsapix.spider.eastmoney as cnsource
from tsapix.tools.taskbase import exe_time_limit, free_memory

import logging
import os
import time

tuiv = read_yaml_file(code_univ_save_path)
tuiv = tuiv[:5] # take 5 tickers for illustration
print("Number of China tickers:", len(tuiv))
single_task_timelmt = 60 * 60 * 10

for a, b in [
    ('d', 'bfq'), # meaning [daily, unadjusted]
    # ('30min', 'bfq'),
    # ('60min', 'bfq'),
]:
    print("Ingesting data @", a, b)
    try:
        with exe_time_limit(single_task_timelmt):
            xobj = cnsource.HistPX(a, b, tickers=tuiv, start="2011-12-31", end=date.today().strftime("%Y-%m-%d"), lmt='1000000')
            xobj.download(chunk_size=200)

            xobj.get_cube_and_save(pairname=f'histpx_{a}_{b}', froot=cube_warehouse_root)
    except Exception as e:
        logging.error(e)
```

>[!WARNING]
>Current data source of China Market are based on open APIs, pay attention to your ingestion speed. 
>If speed exceed website limit, empty files will be returned.
><br><br>Current default speed is reasonable for the website but slow, 4000+ tickers need around 4 hours. Be patient.

>[!TIP]
>If you need to ingest data for all the tickers (4000+), leave it to run at spare time. In this case, you may use the environment primarily for backtest.
><br><br>If you have a subset of tickers, especially if the number is below 200, it can be fast. In this case, you may get live data during trading hours; or you may export the target tickers to your broker's app, where you can get live data in the market open time.

#### 2. China Market - News
Examples of building Apps based on TSApiX wrapped Sina News API can be found [here](https://github.com/mengyuan007/tsapix/blob/main/_sample/spider_SinaNews_keyword_screening.ipynb) and [here](https://github.com/mengyuan007/tsapix/blob/main/_sample/spider_SinaNews_dashboard.py).  
##### Example
```
from tsapix.spider.sina_keyword_screening import *

keyword='特朗普'
_resdict = normal_task_process(
    keyword=keyword, record_target=10, start_page=1, time_limit='2014-03-19 18:38:45')

respd = pd.DataFrame(_resdict).sort_values('id')
respd.head(20)
```

#### 3. US Market - IBKR
Follow [this page](https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/#api-introduction) to setup IBKR API. 
<br><br>Please put ```IBJts``` and ```META-INF``` folders under [tsapix/ibkr/twsapi](https://github.com/mengyuan007/tsapix/tree/main/src/tsapix/ibkr/twsapi)
<img width="564" height="141" alt="22 May 2025, 1118" src="https://github.com/user-attachments/assets/d784ec53-c34b-470e-88d7-ed9bcd7d0047" />
<br>
Examples of using TSApiX wrapped IBKR API can be found [here](https://github.com/mengyuan007/tsapix/blob/main/_sample/ibkr_data_QQQ_options.ipynb) and [here](https://github.com/mengyuan007/tsapix/blob/main/_sample/ibkr_data_QQQ_OHLCV.ipynb).
##### Example
```
from tsapix.envbase import *
from tsapix.utils import env_db_root
from tsapix.ibkr.qqq import *

app = DataApp()
app.connect("127.0.0.1", 4001, 1)
threading.Thread(target=app.run).start()
time.sleep(5)

ltdlist = [f"{xdt} 16:00:00 US/Eastern" for xdt in [
    (datetime.datetime.today() - datetime.timedelta(x)).strftime("%Y%m%d") for x in range(1, 2)
]]
barsetting = [("1 D", "1 min", "TRADES")]
# barsetting = [("1 D", "5 mins", "TRADES")]

from itertools import product

_reqlist = list(product(ltdlist, barsetting))

paramslog = {}

from tqdm import tqdm

for _req in tqdm(_reqlist):
    _ltd, _bst = _req
    _ltddate = _ltd.split(" ")[0]
    _contract = init_qqq()

    _reqid = app.nextId()
    paramslog[_reqid] = [_ltd, _bst, _ltddate]
    print("Processing", _reqid, paramslog[_reqid])
    app.reqHistoricalData(_reqid, _contract, _ltd, _bst[0], _bst[1], _bst[2], 1, 1, False, [])
```

### :clock2: Maintenance
Database needs to be updated to include new information.
You can write a task script and schedule it to run at expected frequency.

### :clock3: Load Environment to Play
A sample loading China Market Environment can be found [here](https://github.com/mengyuan007/tsapix/blob/main/_sample/playgroud_China.ipynb).

##### Example
```
from tsapix.envbase import *
from tsapix.spider.eastmoney import HistPX
from tsapix.dimvals import maps, code_name_mapdict, load_maps, load_histpx_cubes

histpx = load_histpx_cubes([
    ('d', 'bfq'), # Make sure you have downloaded this data in your environment, i.e. daily & unadjusted
])
xobj = histpx['d_bfq']
xpd = xobj['Close']
```

>[!NOTE]
>China Market structured data were stored as **Cube** in the environment. It has three dimensions, which are Time, Tickers, and Features (OHLCV etc.).
>The reason for using this structure is to utilise vectorised computing in Python.
><br><br>
>All the environment data are supposed to be stored in Cube based structure for computing performance unless new technology with better perf be discovered / adopted in the future. Currently only China Market was stored in this way.

### :clock4: Toolkits for your Play
```tsapix==0.0.1``` is primarily for environment creation, some basic toolkits have been added. Advanced toolkits have not been purified to publish, they will be added in following versions, these include: 
- autoML framework for AI/Machine Learning enthusiasts, easy the process of feature engineering and model selection
- backtest framework to assemble strategy and get historic performance
- perfPannel to track live performance of strategies
- ...
