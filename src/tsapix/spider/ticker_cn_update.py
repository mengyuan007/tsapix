from tsapix.utils import *
from tsapix.utils import icloud_froot, env_db_root, code_univ_save_path
from tsapix.utils import save_as_yaml, read_yaml_file


sh_sec_common_headers = {
    'Referer': 'https://www.sse.com.cn/'
}

def update_cn_ticker_universe(
        sh_code_rawf_path = env_db_root+"sh_a_code.xls",
        sz_code_rawf_path = env_db_root+'sz_a_code.xlsx',
):
    # SH Code

    # sh_code_rawf_path = "sh_a_code.xls"

    import requests

    xls_url = """https://query.sse.com.cn/sseQuery/commonExcelDd.do?sqlId=COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L&type=inParams&CSRC_CODE=&STOCK_CODE=&REG_PROVINCE=&STOCK_TYPE=1&COMPANY_STATUS=2,4,5,7,8"""
    xres = requests.get(xls_url, headers={
        'Referer': 'https://www.sse.com.cn/'
    })

    with open(sh_code_rawf_path, 'wb') as f:
        f.write(xres.content)

    sh_code_univlist = [str(x) for x in pd.read_excel(sh_code_rawf_path).iloc[:, 0].values]
    print('Shanghai', len(sh_code_univlist))

    # SZ Code

    # pip install openpyxl --upgrade

    # sz_code_rawf_path = 'sz_a_code.xlsx'

    xlsx_url = """http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&random=0.2520163050277727"""
    xres = requests.get(xlsx_url, headers={
    #     'Referer': 'http://www.szse.cn/'
    })

    with open(sz_code_rawf_path, 'wb') as f:
        f.write(xres.content)

    def sz_code_helper(x):
        if len(x)<6:
            return '0'*(6-len(x))+x
        return x

    sz_code_univlist = [sz_code_helper(str(x)) for x in pd.read_excel(sz_code_rawf_path).iloc[:, 4].values]
    print('Shenzhen', len(sz_code_univlist))

    # CN Code Universe

    a_code_univlist = sh_code_univlist + sz_code_univlist
    print('CN Universe', len(a_code_univlist))

    # Save as .yaml

    # code_univ_save_path = icloud_froot + 'share/' + 'a_code_univ.yaml'
    print('Universe file save path: ', code_univ_save_path)
    save_as_yaml(code_univ_save_path, a_code_univlist)

    # return a_code_univlist


# 上海证券交易所函数 指数代码不同
def get_sh_index_constituents(xindex_code, save_path_root=env_db_root, sh_sec_common_headers=sh_sec_common_headers):
    xurl = f"""http://query.sse.com.cn/commonSoaQuery.do?jsonCallBack=&sqlId=DB_SZZSLB_CFGLB&indexCode={xindex_code}&isPagination=false&_="""
    xres = requests.get(xurl, headers=sh_sec_common_headers)
    xconstituents = [str(x) for x in pd.DataFrame(json.loads(xres.text)['pageHelp']['data'])['securityCode'].values]

    xsave_path = save_path_root + f'constituents_{xindex_code}.yaml'
    save_as_yaml(xsave_path, xconstituents) # only contain live code
    print(len(xconstituents), xsave_path)
    
    xsave_path2 = save_path_root + f'constituentshist_{xindex_code}.yaml'
    xreslist = json.loads(xres.text)['pageHelp']['data']
    try:
        xreslist += read_yaml_file(xsave_path2)
    except FileNotFoundError:
        pass
    save_as_yaml(xsave_path2, xreslist)
    print(len(xreslist), xsave_path2)
    return xsave_path, xconstituents, xsave_path2, xreslist

def get_sh_index_stat(xindex_code, save_path_root=env_db_root, sh_sec_common_headers=sh_sec_common_headers):
    xurl = f"""http://query.sse.com.cn/commonSoaQuery.do?&jsonCallBack=&isPagination=false&sqlId=DB_SZZSLB_QZHYLB&indexCode={xindex_code}&_="""
    xres = requests.get(xurl, headers=sh_sec_common_headers)
    
    xreslist = json.loads(xres.text)['pageHelp']['data']
    xsave_path = save_path_root + f'stat_{xindex_code}.yaml'
    try:
        xreslist += read_yaml_file(xsave_path)
    except FileNotFoundError:
        pass
    save_as_yaml(xsave_path, xreslist)

    print(len(xreslist), xsave_path)
    return xsave_path, xreslist


