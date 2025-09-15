import requests
from tsapi.utils import icloud_froot, save_as_yaml
import os

def get_nasdaq100_constituents(savepath=icloud_froot + "share/"):
    # headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"}
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.nasdaq.com",
        "Referer": "https://www.nasdaq.com/",
    }
    res=requests.get("https://api.nasdaq.com/api/quote/list-type/nasdaq100",headers=headers)
    main_data=res.json()['data']['data']['rows']

    nasdaq100_tickerpool = []
    for i in range(len(main_data)):
        print(main_data[i]['symbol'], end=" ")
        nasdaq100_tickerpool.append(main_data[i]['symbol'])

    if savepath is not None:
        save_as_yaml(os.path.join(savepath, "nasdaq100_tickerpool.yaml"), nasdaq100_tickerpool)
    return nasdaq100_tickerpool