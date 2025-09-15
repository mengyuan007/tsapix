
import os
import time
from tsapix.utils import icloud_froot, env_db_root, cube_warehouse_root, _log_froot, env_raw_root
import tsapix
from tsapix.utils import *

#1.##################### initiate folders to store data ######################
print("###################### Initiate folders to store data...")
for fld in [icloud_froot, env_db_root, cube_warehouse_root, _log_froot, env_raw_root]:
    os.makedirs(fld, exist_ok=True)
    print(fld)

time.sleep(5)


#2.##################### Initiate China tickers ######################
print("###################### Initiate China tickers ...")
from tsapix.spider.ticker_cn_update import update_cn_ticker_universe
import tsapix.spider.eastmoney as cnsource

try:
    update_cn_ticker_universe()

    cnsource.eastmoney_query_ST_names(savepath=env_db_root)

except:
    print("Failed!")

#2.1##################### China tickers meta data ######################
print("###################### Meata data: Industry")
cnsource.eastmoney_industry_info_downloader()
print("###################### Meata data: Concept")
cnsource.eastmoney_concept_info_downloader()
print("###################### Meata data: Geo")
cnsource.eastmoney_geo_info_downloader()

print("###################### Generating Meata data Dict...")
a_univ_list = read_yaml_file(code_univ_save_path)
cnsource.get_stock_meta_data(a_univ_list, dbroot=env_raw_root, save_dbroot=env_db_root)


# #3.##################### Initiate China Data Base ######################
# print("###################### Initiate China Data Base ...")
# from tsapix.tools.taskbase import exe_time_limit, free_memory
# import logging
# import gc

# import tsapix.spider.eastmoney as cnsource


# tuiv = read_yaml_file(code_univ_save_path)
# tuiv = tuiv[:5]
# print("Number of China tickers:", len(tuiv))
# single_task_timelmt = 60 * 60 * 10

# for a, b in [
#     ('d', 'bfq'), # meaning [daily, unadjusted]
#     # ('30min', 'bfq'),
#     # ('60min', 'bfq'),
# ]:
#     print("Ingesting data @", a, b)
#     try:
#         with exe_time_limit(single_task_timelmt):
#             xobj = cnsource.HistPX(a, b, tickers=tuiv, start="2011-12-31", end=date.today().strftime("%Y-%m-%d"), lmt='1000000')
#             xobj.download(chunk_size=200)

#             xobj.get_cube_and_save(pairname=f'histpx_{a}_{b}', froot=cube_warehouse_root)
#     except Exception as e:
#         logging.error(e)

#     free_memory([xobj,])
#     time.sleep(40)

# import beepy
# beepy.beep(6)