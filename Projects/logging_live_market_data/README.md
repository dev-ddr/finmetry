# Live market data logging

Live market feed and depth data for NIFTY50 and BANKNIFTY stocks are logged here. Along with option chain data for all the stocks. For this, first the symbols of the stocks consisting of NIFTY50 and BANKNIFTY is to be downloaded.


```python
import datetime as dtm
import time
t1 = dtm.datetime(2023,8,10,9,13,0)
now_time = dtm.datetime.now()
while now_time < t1:
    time.sleep(1)
    now_time = dtm.datetime.now()
```


```python
import finmetry as fm
import pandas as pd
import numpy as np
import datetime as dtm
import os
import time

# market_data_foldpath = r"X:\finmetry"
```

# Run this cell for waiting


```python
t1 = dtm.datetime(2023,8,11,9,14,30)
now_time = dtm.datetime.now()
while now_time < t1:
    time.sleep(1)
    now_time = dtm.datetime.now()
```

## Logging into Client5paisa


```python
### initializing scrip_master
scrip_master_filepath = os.path.join(market_data_foldpath, "scrip_master.csv")
scrip_master = fm.client_5paisa.ScripMaster()
scrip_master.save(scrip_master_filepath)
scrip_master = fm.client_5paisa.ScripMaster(filepath=scrip_master_filepath)
### logging in
c_5p = fm.client_5paisa.Client5paisa(
    email=email, password=password, dob=dob, cred=cred, scrip_master=scrip_master
)
```

     09:14:41 | Logged in!!
    

### Loading the symbols for NIFTY and BANKNIFTY stocks

NSE provides the list of symbols for NIFTY50 and BANKNIFTY. All the data is stored in `other_folder`, hence here the data is read from there.


```python
### loading banknifty list
syms = pd.read_csv("../other_data/ind_niftybanklist.csv")['Symbol'].to_list()
syms.pop(syms.index('BANKBARODA'))

### loading nifty50 stocks
syms1 = pd.read_csv("../other_data/ind_nifty50list.csv")['Symbol'].to_list()
syms1 = []

### only adding those symbols which are not there
for sym in syms1:
    if sym not in syms:
        syms += [sym]
    else:
        pass
        # print(sym,'already there')

### adding NIFTY and BANKNIFTY symbols to it
syms += ['NIFTY', 'BANKNIFTY']

### inititalizing the Stock class for all
sl1 = []
for sym in syms:
    s1 = fm.Stock(symbol=sym,exchange="N",exchange_type="C",store_local=True,local_data_foldpath=market_data_foldpath)
    sl1.append(s1)

sm1 = scrip_master.get_scrip(sl1)
```

### Loading the Derivatives for all the Stocks

Derivatives/ Options for all the stocks can be obtained from option chain. Here, the latest option chain is only considered. For equities, latest monthly expiry is considered and for indices latest weekly and latest monthly expiry is considered. The amount of data will become huge if we download the whole option chain for each symbols. Hence only the 3 or 4 in-the-money and 3-4 out-of-money options are chosen for logging.

To know in-the-money or out-of-money options, LTP of undeerlying is also required. Hence first the LTP for all the Symbols will be downloaded.


```python
### getting expiry dates
monthly_expiry = c_5p.get_monthly_option_expiry()['Date'].iloc[0].strftime("%Y-%m-%d")
update_option_chain = True
n_strikes = 7
weekly_expiry = c_5p.get_weekly_option_expiry()['Date'].iloc[0].strftime("%Y-%m-%d")
```


```python
### getting the LTP for all the stocks
ltps = c_5p.get_market_depth(sl1).set_index('Symbol')['LastTradedPrice'].to_dict()

### iterating over all the LTPS.
for isym in ltps:
    ### iterating over all the stocks
    for s1 in sl1:
        ### if symbols match then
        if s1.symbol == isym:
            ### get opion chain
            op_chain = c_5p.get_option_chain(s1,monthly_expiry,update=update_option_chain)
            ### getting the strike rates of required options
            strike_rates = op_chain['StrikeRate'].unique()
            strike_rates.sort()
            ### giving less than or equal to for inclusion of at-the-money strike rate
            f1 = strike_rates <= ltps[s1.symbol]
            s1.strike_rates = list(strike_rates[f1][-n_strikes:])
            f1 = strike_rates > ltps[s1.symbol]
            s1.strike_rates += list(strike_rates[f1][:n_strikes])
            ### creating the option names from strike price
            ### spliting one name then creating all the name from it by replacing the last value of strike rate and second last value of CE/PE
            symbol1 = " ".join(op_chain['Name'].iloc[0].split(' ')[:-2])
            s1.option_symbols = [symbol1 + " CE "+format(sr,'.2f') for sr in s1.strike_rates] + [symbol1 + " PE "+format(sr,'.2f') for sr in s1.strike_rates]

if monthly_expiry != weekly_expiry:
    for isym in ltps:
        for s1 in sl1:
            if (s1.symbol == isym) and (s1.symbol in ['NIFTY','BANKNIFTY']):
                op_chain = c_5p.get_option_chain(s1,weekly_expiry,update=True)
                ### getting the strike rates of required options
                strike_rates = op_chain['StrikeRate'].unique()
                strike_rates.sort()
                f1 = strike_rates <= ltps[s1.symbol]
                s1.strike_rates = list(strike_rates[f1][-(n_strikes+2):])
                f1 = strike_rates > ltps[s1.symbol]
                s1.strike_rates += list(strike_rates[f1][:(n_strikes+2)])
                ### creating the option names from strike price
                ### spliting one name then creating all the name from it by replacing the last value of strike rate and second last value of CE/PE
                symbol1 = " ".join(op_chain['Name'].iloc[0].split(' ')[:-2])
                s1.option_symbols += [symbol1 + " CE "+format(sr,'.2f') for sr in s1.strike_rates] + [symbol1 + " PE "+format(sr,'.2f') for sr in s1.strike_rates]
```

adding all the symbols of stocks and its options to create single list for data acquisition. Here, the `store_local=False` because the data is first stored in one file. Then after market-hours, the data will be segregated into different Stocks.


```python
sl2 = []
for s1 in sl1:
    s2 = fm.Stock(symbol=s1.symbol,exchange="N",exchange_type="C",store_local=False)
    sl2 += [s2]
    for sym in s1.option_symbols:
        s2 = fm.Stock(symbol=sym,exchange="N",exchange_type="D",store_local=False)
        sl2 += [s2]
sm2 = scrip_master.get_scrip(sl2)
```

# Saving live market data

## Defining functions for getting and storing the data


```python
from websocket import create_connection
import json

### data saving
def append_it_blind(data: pd.DataFrame, filepath: str) -> None:
    try:
        df1 = pd.read_pickle(filepath)
        df1 = pd.concat([data, df1])
        df1.to_pickle(filepath)
        return
    except FileNotFoundError as e:
        print(f"Creating the file - {filepath}")
        data.to_pickle(filepath)
        return


### getting the live data
def get_live_data(m_list: list[dict], feed_type: str) -> pd.DataFrame:
    mf_list = c_5p.Request_Feed(feed_type, "s", m_list)
    c_5p.ws_feed = create_connection(c_5p._web_url1)
    c_5p.ws_feed.send(json.dumps(mf_list))
    d1 = ""
    if feed_type == "md":
        for s in mf_list["MarketFeedData"]:
            d1 = d1 + ",{" + c_5p.ws_feed.recv()[1:-1] + "}"
    if feed_type == "mf":
        for s in mf_list["MarketFeedData"]:
            d1 = d1 + "," + c_5p.ws_feed.recv()[1:-1]
    c_5p.ws_feed.close()
    d1 = "[" + d1[1:] + "]"
    return pd.DataFrame(json.loads(d1))


def get_market_depth(md_list: list[dict]) -> pd.DataFrame:
    d1 = pd.DataFrame(c_5p.fetch_market_depth_by_symbol(md_list)["Data"])
    d1["Datetime"] = dtm.datetime.now()
    return d1[
        [
            "BuyQuantity",
            "LastQuantity",
            "LastTradeTime",
            "LastTradedPrice",
            "OpenInterest",
            "ScripCode",
            "SellQuantity",
            "TotalBuyQuantity",
            "TotalSellQuantity",
            "Volume",
            "Datetime",
        ]
    ]


```


```python
### data folder
# saving_foldpath = r"F:\finmetry\market_live_data"
saving_foldpath = r'C:\Users\GTCRL\Indian Institute of Science\We Will - Documents\General\market\Finmetry\data\market_live_data'

date = dtm.datetime.now().strftime("%Y%m%d") + '_data'
data_foldpath = os.path.join(saving_foldpath,date)
fm.make_dir(data_foldpath)

feed_type = "md"
m_list = sm2.rename(columns={"Scripcode": "ScripCode"})[["Exch", "ExchType", "ScripCode"]].to_dict(orient="records")

md_list = sm2.rename(columns={"Exch": "Exchange", "ExchType": "ExchangeType"})[["Exchange", "ExchangeType", "Symbol"]].to_dict(orient="records")
```

# All ready for Live logging

For live logging, output widget will be used for printing the information.


```python
from ipywidgets import Output
out1 = Output(layout={'border': '1px solid black'})


@out1.capture()
def print_and_save(avg_time,counts,max_time,min_time):
    t1 = time.time()
    d1 = get_market_depth(md_list)
    fname = dtm.datetime.now().strftime("%Y%m%d_%H%M") + '_data.pickle'
    append_it_blind(d1,os.path.join(data_foldpath,fname))
    dt = time.time() - t1
    avg_time = (avg_time*counts + dt)/(counts+1)
    counts += 1
    if max_time<dt:
        max_time = dt
    if min_time>dt:
        min_time = dt
    out1.clear_output()
    print('Number of counts =' ,counts)
    print('absolute time =' ,dt,'sec')
    print('average time =' ,avg_time,'sec')
    print('max_time time =' ,max_time,'sec')
    print('min_time time =' ,min_time,'sec')
    print('*'*100)
    print(d1.shape)
    return avg_time,counts,max_time,min_time

out1
```


    Output(layout=Layout(border='1px solid black'))



```python
avg_time = 0
counts = 0
max_time = -1000
min_time = 1000
market_start_time = dtm.time(9,15)
market_end_time = dtm.time(15,31)

### this will wait till the market starting time
now_time = dtm.datetime.now().time()
while (now_time < market_start_time):
    time.sleep(0.1)
    now_time = dtm.datetime.now().time()

n_tries = 3
tries = 1
while (now_time < market_end_time) and (tries < n_tries):
    try:
        avg_time,counts,max_time,min_time = print_and_save(avg_time,counts,max_time,min_time)
        tries = 1
    except:
        tries += 1
    now_time = dtm.datetime.now().time()
```

# Reading the data


```python
# data_foldpath = r'X:\finmetry'
files_path = fm.get_file_path(data_foldpath)
data = pd.DataFrame()
for fp in files_path:
    data = pd.concat([data,pd.read_pickle(fp)])
```

## Saving the data to market_data_foldpath

The data is saved inside the folder of underlying. Multiple sub-folders for each options is created


```python
scripcodes = data['ScripCode'].unique()
for scripcode in scripcodes:
    f1 = scrip_master.data['Scripcode'] == scripcode
    scrip = scrip_master.data[f1]

    exch = scrip['Exch'].iloc[0]
    exchtype = scrip['ExchType'].iloc[0]
    ### if the scrip is options then it should be stored inside the underlying symbols folder
    if exchtype == 'D':
        s2_0 = fm.Stock(symbol=scrip['Root'].iloc[0],exchange='N',exchange_type='C',store_local=True, local_data_foldpath=market_data_foldpath)
        s2 = fm.Stock(symbol=scrip['Symbol'].iloc[0],exchange=exch,exchange_type=exchtype,store_local=True, local_data_foldpath=s2_0.local_data_foldpath)
    else:
        s2 = fm.Stock(symbol=scrip['Symbol'].iloc[0],exchange=exch,exchange_type=exchtype,store_local=True, local_data_foldpath=market_data_foldpath)

    f1 = data['ScripCode'] == scripcode
    s2.market_depth_data = data[f1].set_index('Datetime')
    fname = s2.market_depth_data.index[0].strftime('%Y%m%d') + '_market_depth.pickle'
    path1 = os.path.join(s2.local_data_foldpath, fname)
    s2.market_depth_data.to_pickle(path1)
```

## Saving the data ScripCode wise into different folder

First searching the name of the scrip from scrip master and then making its folder and saving the data
market_depths_foldpath = r'F:\finmetry\market_depth_data'

scripcodes = data['ScripCode'].unique()
for scripcode in scripcodes:
    f1 = scrip_master.data['Scripcode'] == scripcode
    scrip = scrip_master.data[f1]

    exch = scrip['Exch'].iloc[0]
    exchtype = scrip['ExchType'].iloc[0]
    ### if the scrip is options then it should be stored inside the underlying symbols folder
    if exchtype == 'D':
        s2_0 = fm.Stock(symbol=scrip['Root'].iloc[0],exchange='N',exchange_type='C',store_local=True, local_data_foldpath=market_depths_foldpath)
        s2 = fm.Stock(symbol=scrip['Symbol'].iloc[0],exchange=exch,exchange_type=exchtype,store_local=True, local_data_foldpath=s2_0.local_data_foldpath)
    else:
        s2 = fm.Stock(symbol=scrip['Symbol'].iloc[0],exchange=exch,exchange_type=exchtype,store_local=True, local_data_foldpath=market_depths_foldpath)

    f1 = data['ScripCode'] == scripcode
    s2.market_depth_data = data[f1].set_index('Datetime')
    fname = s2.market_depth_data.index[0].strftime('%Y%m%d') + '_depth.pickle'
    path1 = os.path.join(s2.local_data_foldpath, fname)
    s2.market_depth_data.to_pickle(path1)
---
---
