# Downloading the historical data for NSE futures stocks

The stocks symbols of NSE futures stocks are read from local .csv file. The code downloads the data in '1m', '5m' and '1d' time frame in steps. It was observed that code gives error when large amount of data is downloaded. It takes huge time and code gives timeouterror. Hence, the data is downloaded in months wise.


```python
import finmetry as fm
import pandas as pd
import numpy as np
import datetime as dtm
import os

# market_data_foldpath = r"X:\finmetry"
```

## Logging into Client5paisa


```python
### initializing scrip_master
scrip_master_filepath = os.path.join(market_data_foldpath, "scrip_master.csv")
# scrip_master = fm.client_5paisa.ScripMaster()
# scrip_master.save(scrip_master_filepath)
scrip_master = fm.client_5paisa.ScripMaster(filepath=scrip_master_filepath)
### logging in
c_5p = fm.client_5paisa.Client5paisa(
    email=email, password=password, dob=dob, cred=cred, scrip_master=scrip_master
)
```

     18:42:36 | Logged in!!
    

---
---
### Loading NSE futures stocklist

Reading the Symbols from `all_nse.csv` file from which the list of `Stock` class will be generated.


```python
symbols = pd.read_csv("all_nse.csv")["symbol"].to_list()
sl1 = []
for sym in symbols:
    s1 = fm.Stock(
        symbol=sym.upper(),
        exchange="N",
        exchange_type="C",
        store_local=True,
        local_data_foldpath=market_data_foldpath,
    )
    sl1.append(s1)
sm1 = scrip_master.get_scrip(sl1)
```

The start and end date for all the data downloading.


```python
start = dtm.datetime(2023, 4, 15)
end = dtm.datetime(2023, 8, 1)
```

## Downloading 1min data

Here, the timeinterval between start and end date is kept as 30 days.


```python
dt1 = start
while dt1 <= end:
    start_date = dt1
    end_date = dt1 + dtm.timedelta(days=30)
    for s1 in sl1:
        n_try = 0
        while n_try < 20:
            try:
                c_5p.download_historical_data(stocklist=[s1], interval="1m", start=start_date, end=end_date)
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                n_try += 1
                print(n_try)
    dt1 = end_date
```

## Downloading 5min data

Here, the timeinterval between start and end date is kept as 90 days.


```python
dt1 = start
while dt1 <= end:
    start_date = dt1
    end_date = dt1 + dtm.timedelta(days=90)
    for s1 in sl1:
        n_try = 0
        while n_try < 20:
            try:
                c_5p.download_historical_data(stocklist=[s1], interval="5m", start=start_date, end=end_date)
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                n_try += 1
                print(n_try)
    dt1 = end_date
```

## Downloading 1Day data

Here, data is downloaded in one go.


```python
for s1 in sl1:
    n_try = 0
    while n_try < 20:
        try:
            c_5p.download_historical_data(stocklist=[s1], interval="1d", start=start, end=end)
            break
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            n_try += 1
            print(n_try)
```

---
---

# Downloading data for Various Index


```python
symbols = ['NIFTY', 'BANKNIFTY', 'GOLDBEES', 'INDIA VIX']
exchs = ['N','N', 'N', 'N']
exchs_type = ['C','C', 'C', 'D']
sl1 = []
for sym,e,et in zip(symbols,exchs,exchs_type):    
    s1 = fm.Stock(symbol=sym,exchange=e,exchange_type=et,store_local=True,local_data_foldpath=market_data_foldpath)
    sl1.append(s1)

nifty_sectors = ['NIFTY IT','NIFTY REALTY','NIFTY INFRA','NIFTY ENERGY','NIFTY FMCG','NIFTY MNC','NIFTY PHARMA','NIFTY PSE','NIFTY PSU BANK','NIFTY SERV SECTOR','NIFTY PVT BANK','NIFTY AUTO','FINNIFTY','NIFTY METAL','NIFTY HEALTHCARE','NIFTY OIL AND GAS','NIFTY TOTAL MARKET','NIFTY INDIA DIGITAL','NIFTYMEDIA']
nifty_gsecs = ['NIFTY GS 10YR','NIFTY GS 4 8YR','NIFTY GS 11 15YR','NIFTY GS 15YRPLUS','NIFTY GS COMPSITE']
for sym in nifty_sectors+nifty_gsecs:
    s1 = fm.Stock(symbol=sym,exchange="N",exchange_type="C",store_local=True,local_data_foldpath=market_data_foldpath)
    sl1.append(s1)

sm1 = scrip_master.get_scrip(sl1)

### start and end dates
# start = dtm.datetime(2019, 4, 1)
# end = dtm.datetime(2023, 4, 19)
```


```python
### 1 min data
dt1 = start
while dt1 <= end:
    start_date = dt1
    end_date = dt1 + dtm.timedelta(days=30)
    for s1 in sl1:
        n_try = 0
        while n_try < 20:
            try:
                c_5p.download_historical_data(stocklist=[s1], interval="1m", start=start_date, end=end_date)
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                n_try += 1
                print(n_try)
    dt1 = end_date

### 5 min data
dt1 = start
while dt1 <= end:
    start_date = dt1
    end_date = dt1 + dtm.timedelta(days=90)
    for s1 in sl1:
        n_try = 0
        while n_try < 20:
            try:
                c_5p.download_historical_data(stocklist=[s1], interval="5m", start=start_date, end=end_date)
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                n_try += 1
                print(n_try)
    dt1 = end_date


### daily data
for s1 in sl1:
    n_try = 0
    while n_try < 20:
        try:
            c_5p.download_historical_data(stocklist=[s1], interval="1d", start=start, end=end)
            break
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            n_try += 1
            print(n_try)
```

---
---
