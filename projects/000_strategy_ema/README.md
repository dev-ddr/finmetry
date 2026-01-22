# Imports


```python
import pandas as pd
import numpy as np
import datetime as dtm
from typing import List
import finmetry as fm
```

# Paths


```python
LOCAL_DATA_FOLDPATH = "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/historical_data"
stocklist_foldpath = "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/list_of_symbols/futures_traded_symbols.txt"
```

# Defining Stock universe of Strategy

Its a list of symbols


```python
with open(stocklist_foldpath, "r") as f:
    symbols = [line.strip() for line in f if line.strip()]
syms = symbols[:100]
# syms = ["RELIANCE", "IDEA", "TCS", "INFY", "ITC", "KOTAKBANK", "TRENT", "LICHSGFIN", "LUPIN", "RAMCOCEM", "MFSL"]

print(syms[:3])
```

    ['ABB', 'ATUL', 'BAJFINANCE']


### Initialize the stockdict object

Stockdict object provides an interface to access stocks from etither its symbol or an integer index. We can iterate over stockdict like a list.


```python
sd1 = fm.StockDict()
for sym in syms:
    sd1.add(fm.Stock(symbol=sym))
```

# Strategy


```python
%load_ext autoreload
%autoreload 2
from strategy import EMI, EMIDataLoader
```

### Strategy

Initialize strategy based on its configuration/attributes.


```python
stg1 = EMI(top_n=2, holding_period=5, stoploss=0.05, target=0.05)
```

### Strategy Dataloader

Dataloader gives the OHLCV and the computed features for any given timestamp between the start and end date. Various feature conputation parameters goes in here.


```python
dl1 = EMIDataLoader(stockdict=sd1, start_date="2025-01-01", end_date="2025-06-01", fast_window=21, slow_window=51)
```


```python
stg1(dl1["2025-03-03"])
```




    [Order(timestamp=datetime.datetime(2025, 3, 3, 0, 0), symbol='HDFCBANK', price=np.float64(850.78), order_type=<ORDERTYPE.buy: 'buy'>, value_frac=0.5, id='71db75c8-daa2-4cb5-b49e-40020cc18bf1', target=np.float64(893.319), stop_loss=np.float64(808.241), hold_uptill=datetime.datetime(2025, 3, 8, 0, 0), remarks='EMA gap=0.1731', fill_price=None, fill_qty=None, fill_timestamp=None, fill_remarks=None, brokerage_cost=0, total_cost=None, account_idx=0)]



# Backtesting

### Initialize portfolio

The portfolio requires:-
- `starting_cash` -  keeping it to 100 for ease of calculations
- `total_accounts` - numbers of isolated accounts. Cash is devided equally amongst all accounts at first.
- `executioner` - for added market noise. However, here it is not doing anyting.


```python
portfolio = fm.Portfolio(starting_cash=100, total_accounts=stg1.total_accounts, executioner=fm.executioners.ExecutionModel())
```

### Initialize backtester

It needs data-loader, strategy and portfolio. Backteste simply iterates over all data from data_loader.


```python
tester = fm.Backtester(data_loader=dl1, strategy=stg1, portfolio=portfolio)
```

### Run the test


```python
tester.run()
```

## Analyzing results

### Porfolio valuation with time

You can add banchmark here to compare your strategy with it.


```python
portfolio.account_history
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>value</th>
    </tr>
    <tr>
      <th>timestamp</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2025-01-01</th>
      <td>100.000000</td>
    </tr>
    <tr>
      <th>2025-01-02</th>
      <td>100.000000</td>
    </tr>
    <tr>
      <th>2025-01-03</th>
      <td>100.000000</td>
    </tr>
    <tr>
      <th>2025-01-06</th>
      <td>99.743784</td>
    </tr>
    <tr>
      <th>2025-01-07</th>
      <td>99.589693</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
    </tr>
    <tr>
      <th>2025-05-26</th>
      <td>99.163746</td>
    </tr>
    <tr>
      <th>2025-05-27</th>
      <td>99.042506</td>
    </tr>
    <tr>
      <th>2025-05-28</th>
      <td>99.039004</td>
    </tr>
    <tr>
      <th>2025-05-29</th>
      <td>99.096298</td>
    </tr>
    <tr>
      <th>2025-05-30</th>
      <td>98.940035</td>
    </tr>
  </tbody>
</table>
<p>101 rows × 1 columns</p>
</div>



### Arranged order book

Arranges entry and exit orders in single row indexes by order-id. You can analyze, how many orders were positive and all.


```python
portfolio.arranged_order_book.tail(20)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>buy_symbol</th>
      <th>buy_fill_price</th>
      <th>buy_fill_qty</th>
      <th>buy_fill_timestamp</th>
      <th>buy_total_cost</th>
      <th>buy_account_idx</th>
      <th>buy_hold_uptill</th>
      <th>buy_remarks</th>
      <th>sell_symbol</th>
      <th>sell_fill_price</th>
      <th>sell_fill_qty</th>
      <th>sell_fill_timestamp</th>
      <th>sell_total_cost</th>
      <th>sell_account_idx</th>
      <th>sell_hold_uptill</th>
      <th>sell_remarks</th>
    </tr>
    <tr>
      <th>id</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>3278d06e-e5cb-4f67-bfa9-0910bfa078d9</th>
      <td>TITAN</td>
      <td>3365.20</td>
      <td>0.001426</td>
      <td>2025-04-25</td>
      <td>4.800263</td>
      <td>4</td>
      <td>2025-04-30</td>
      <td>EMA gap=11.2672</td>
      <td>TITAN</td>
      <td>3379.7000</td>
      <td>0.001426</td>
      <td>2025-04-30</td>
      <td>4.820946</td>
      <td>4.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>7bff72ae-9ba6-4928-94ad-6f6b3330155d</th>
      <td>HEROMOTOCO</td>
      <td>3852.70</td>
      <td>0.002613</td>
      <td>2025-04-29</td>
      <td>10.067450</td>
      <td>1</td>
      <td>2025-05-04</td>
      <td>EMA gap=18.5486</td>
      <td>HEROMOTOCO</td>
      <td>3767.6000</td>
      <td>0.002613</td>
      <td>2025-05-05</td>
      <td>9.845076</td>
      <td>1.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>6cb638f3-63da-40b3-aca1-b73b7e441766</th>
      <td>AARTIIND</td>
      <td>426.65</td>
      <td>0.022173</td>
      <td>2025-05-02</td>
      <td>9.459927</td>
      <td>4</td>
      <td>2025-05-07</td>
      <td>EMA gap=1.3010</td>
      <td>AARTIIND</td>
      <td>447.9825</td>
      <td>0.022173</td>
      <td>2025-05-05</td>
      <td>9.932923</td>
      <td>4.0</td>
      <td>NaT</td>
      <td>target</td>
    </tr>
    <tr>
      <th>2d0169d4-778d-4418-baaa-dcbe0b557af9</th>
      <td>DRREDDY</td>
      <td>1171.30</td>
      <td>0.008778</td>
      <td>2025-05-05</td>
      <td>10.281349</td>
      <td>0</td>
      <td>2025-05-10</td>
      <td>EMA gap=0.0674</td>
      <td>DRREDDY</td>
      <td>1195.6000</td>
      <td>0.008778</td>
      <td>2025-05-12</td>
      <td>10.494648</td>
      <td>0.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>080b66bb-f16a-42dc-892d-a1a291758579</th>
      <td>M&amp;M</td>
      <td>3068.40</td>
      <td>0.003245</td>
      <td>2025-05-06</td>
      <td>9.956263</td>
      <td>1</td>
      <td>2025-05-11</td>
      <td>EMA gap=17.9889</td>
      <td>M&amp;M</td>
      <td>3104.7000</td>
      <td>0.003245</td>
      <td>2025-05-12</td>
      <td>10.074048</td>
      <td>1.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>00b0d453-f51a-4ddd-867f-c966da817a6b</th>
      <td>DEEPAKNTR</td>
      <td>1955.10</td>
      <td>0.002546</td>
      <td>2025-05-06</td>
      <td>4.978131</td>
      <td>1</td>
      <td>2025-05-11</td>
      <td>EMA gap=0.5868</td>
      <td>DEEPAKNTR</td>
      <td>1857.3450</td>
      <td>0.002546</td>
      <td>2025-05-09</td>
      <td>4.729225</td>
      <td>1.0</td>
      <td>NaT</td>
      <td>stop_loss</td>
    </tr>
    <tr>
      <th>4f29ce5a-3629-432f-8dd9-dc187ae9e793</th>
      <td>SUPREMEIND</td>
      <td>3580.10</td>
      <td>0.001451</td>
      <td>2025-05-12</td>
      <td>5.193999</td>
      <td>0</td>
      <td>2025-05-17</td>
      <td>EMA gap=11.2697</td>
      <td>SUPREMEIND</td>
      <td>3759.1050</td>
      <td>0.001451</td>
      <td>2025-05-19</td>
      <td>5.453699</td>
      <td>0.0</td>
      <td>NaT</td>
      <td>target</td>
    </tr>
    <tr>
      <th>73d8baac-5869-4445-a1c4-9d39a0f99b88</th>
      <td>TATAELXSI</td>
      <td>6100.00</td>
      <td>0.001703</td>
      <td>2025-05-12</td>
      <td>10.387998</td>
      <td>0</td>
      <td>2025-05-17</td>
      <td>EMA gap=26.4038</td>
      <td>TATAELXSI</td>
      <td>6245.0000</td>
      <td>0.001703</td>
      <td>2025-05-19</td>
      <td>10.634926</td>
      <td>0.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>e75d405e-70bf-4ae6-b411-bac3aee57f0b</th>
      <td>BHARATFORG</td>
      <td>1203.90</td>
      <td>0.004108</td>
      <td>2025-05-13</td>
      <td>4.945351</td>
      <td>1</td>
      <td>2025-05-18</td>
      <td>EMA gap=8.3510</td>
      <td>BHARATFORG</td>
      <td>1264.0950</td>
      <td>0.004108</td>
      <td>2025-05-16</td>
      <td>5.192619</td>
      <td>1.0</td>
      <td>NaT</td>
      <td>target</td>
    </tr>
    <tr>
      <th>3cd35d40-a289-4ba7-a852-23f608c5542b</th>
      <td>LT</td>
      <td>3567.00</td>
      <td>0.002773</td>
      <td>2025-05-13</td>
      <td>9.890702</td>
      <td>1</td>
      <td>2025-05-18</td>
      <td>EMA gap=11.3444</td>
      <td>LT</td>
      <td>3600.2000</td>
      <td>0.002773</td>
      <td>2025-05-19</td>
      <td>9.982760</td>
      <td>1.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>7f68ceb2-cbd2-46bf-b6d5-30e100ba963b</th>
      <td>KEI</td>
      <td>3398.40</td>
      <td>0.002715</td>
      <td>2025-05-14</td>
      <td>9.227008</td>
      <td>2</td>
      <td>2025-05-19</td>
      <td>EMA gap=26.6454</td>
      <td>KEI</td>
      <td>3461.7000</td>
      <td>0.002715</td>
      <td>2025-05-19</td>
      <td>9.398874</td>
      <td>2.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>81320f6f-f6e1-48c9-abde-b2af804f610f</th>
      <td>HFCL</td>
      <td>85.65</td>
      <td>0.053865</td>
      <td>2025-05-14</td>
      <td>4.613504</td>
      <td>2</td>
      <td>2025-05-19</td>
      <td>EMA gap=0.1790</td>
      <td>HFCL</td>
      <td>89.9325</td>
      <td>0.053865</td>
      <td>2025-05-15</td>
      <td>4.844179</td>
      <td>2.0</td>
      <td>NaT</td>
      <td>target</td>
    </tr>
    <tr>
      <th>3dce841f-8da3-475f-ac60-fed14a0f0345</th>
      <td>HINDCOPPER</td>
      <td>227.78</td>
      <td>0.021389</td>
      <td>2025-05-15</td>
      <td>4.871903</td>
      <td>3</td>
      <td>2025-05-20</td>
      <td>EMA gap=0.3690</td>
      <td>HINDCOPPER</td>
      <td>225.0300</td>
      <td>0.021389</td>
      <td>2025-05-20</td>
      <td>4.813084</td>
      <td>3.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>8a6f04b4-3b1c-41f5-b9b4-ce9b0bae7fbe</th>
      <td>GNFC</td>
      <td>505.20</td>
      <td>0.019287</td>
      <td>2025-05-15</td>
      <td>9.743806</td>
      <td>3</td>
      <td>2025-05-20</td>
      <td>EMA gap=1.6849</td>
      <td>GNFC</td>
      <td>505.6500</td>
      <td>0.019287</td>
      <td>2025-05-20</td>
      <td>9.752486</td>
      <td>3.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>dafa17f8-150a-46fc-9cd2-be3bf2d1afb9</th>
      <td>TATASTEEL</td>
      <td>161.29</td>
      <td>0.060256</td>
      <td>2025-05-22</td>
      <td>9.718737</td>
      <td>3</td>
      <td>2025-05-27</td>
      <td>EMA gap=0.5490</td>
      <td>TATASTEEL</td>
      <td>161.6600</td>
      <td>0.060256</td>
      <td>2025-05-27</td>
      <td>9.741031</td>
      <td>3.0</td>
      <td>NaT</td>
      <td>expiry</td>
    </tr>
    <tr>
      <th>ccb77f0d-767a-411f-8f44-4f32d4987fb1</th>
      <td>INFY</td>
      <td>1580.50</td>
      <td>0.006733</td>
      <td>2025-05-26</td>
      <td>10.641312</td>
      <td>0</td>
      <td>2025-05-31</td>
      <td>EMA gap=6.1906</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4fb01fc6-c024-47cd-be3c-087fc3814bc5</th>
      <td>BATAINDIA</td>
      <td>1278.70</td>
      <td>0.007868</td>
      <td>2025-05-27</td>
      <td>10.060365</td>
      <td>1</td>
      <td>2025-06-01</td>
      <td>EMA gap=1.6951</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4f73a12a-8b5e-4a03-93bb-c4a2ed22790a</th>
      <td>VEDL</td>
      <td>446.85</td>
      <td>0.021099</td>
      <td>2025-05-28</td>
      <td>9.428278</td>
      <td>2</td>
      <td>2025-06-02</td>
      <td>EMA gap=0.0745</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>fee588bc-ea5f-47c1-bd77-0173bbc1b28f</th>
      <td>CUMMINSIND</td>
      <td>3169.40</td>
      <td>0.003070</td>
      <td>2025-05-29</td>
      <td>9.729884</td>
      <td>3</td>
      <td>2025-06-03</td>
      <td>EMA gap=2.3818</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>a270484b-5303-4ded-b192-a45e75f2dbb2</th>
      <td>HINDALCO</td>
      <td>633.50</td>
      <td>0.015306</td>
      <td>2025-05-30</td>
      <td>9.696425</td>
      <td>4</td>
      <td>2025-06-04</td>
      <td>EMA gap=1.2999</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



---
---
