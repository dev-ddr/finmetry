## Installation

You can install finmetry using

```bash
pip install finmetry
```

## Getting Started

This section walks you through a **minimal, end‑to‑end workflow** using `finmetry`.

> This project is developed for my personal use and for my future-self for reference.

By the end of this page, you should clearly understand:

* what you need to implement
* what the framework gives you for free
* how data flows through the system


## Mental Model First

Before writing any code, internalize this loop:

```text
Market Data → Strategy → Orders→ Portfolio → Execution → Accounting
```

The strategy takes in the market data and emits an intention in form of *Order*. You only have to implement till here. Finmetry will take care of backtesting it.

Key rules:

* **Strategies do not know positions or cash**
* **Execution is the only place where market reality is simulated**
* **Portfolio is the report card of the strategy**
* **Backtester only coordinates**

Below is a **complete but minimal working example** using a simple EMA crossover strategy. This example shows how any strategy can be developed.

## Step 0: Prepare Market Data

Download the data to local folder. Refer here for [downloading historical data](https://github.com/dev-ddr/finmetry/tree/base/projects/downloading_historical_data).

Next is, you need to determine the stock universe in which this strategy will work, which is an ensamble of stocks. Like, if your strategy only works on single stock then your stock universe consists of single stock.

```python
syms = ['ABB', 'ATUL', 'BAJFINANCE']
sd1 = fm.StockDict()
for sym in syms:
    sd1.add(fm.Stock(symbol=sym))
```

## EMA Crossover Strategy:- [code link](https://github.com/dev-ddr/finmetry/tree/base/projects/000_strategy_ema)

We will implement exponential moving average strategy to understand all the concepts. There are two major components of a strategy.

1. Feature computation --Outputs--> `MarketGraphData`
1. `MarketGraphData` --Goes into--> Strategy --Outputs--> List of `Order`

### Step 1: Feature Computation

All feature computation happens **outside** the strategy. For this, we have to implement a `fm.StgDataLoader` class and write its `__getitem__` method which will output `MarketGraphData` object.

Responsibilities:

* load historical market data
* compute all features
* return **immutable snapshots**
* No portfolio logic. No trading logic.


```python
class EMADataLoader(fm.StgDataLoader):
    def __init__(self, stockdict, start, end, fast, slow):
        self.stockdict = stockdict
        self.fast = fast
        self.slow = slow

        start = fm.str_to_dtm(start)
        end = fm.str_to_dtm(end)
        shifted_start = start - dtm.timedelta(days=slow + 2)

        self.stockdict.load_historical_data(
            start=shifted_start,
            end=end,
            interval=fm.constants.INTERVAL.one_day,
            local_data_foldpath=LOCAL_DATA_FOLDPATH,
            remove_error_stocks=True,
        )

        self.timestamps = self.stockdict[0].hist_data0.index
        self.timestamps = self.timestamps[self.timestamps >= start]

    def __getitem__(self, ts)->fm.constants.MarketGraphData:
        return get_ema_market_data(
            self.stockdict,
            ts,
            self.fast,
            self.slow,
        )

    def __iter__(self) -> Iterator[fm.constants.MarketGraphData]:
        for ts in self.timestamps:
            yield self[str(ts)]

    def __len__(self):
        return len(self.timestamps)
```

Read more about `MarketGraphData` in [strategy concepts](https://dev-ddr.github.io/finmetry/concepts/strategy_handling_module/#marketgraphdata-data-holder-of-the-market). In above implementation the function `get_ema_market_data` computes all features and returns the `MarketGraphData` for a given timestamp. This produces a **read‑only market snapshot** for a single timestamp and this is the **only place** where data loading and feature computation happens.

Key point:

> **Strategies never compute indicators. They only consume them.**

### Step 2: Strategy — Turning Features into Orders

Now we write the strategy. Notice how **simple** it is.

The strategy:

* reads pre‑computed features
* ranks stocks
* emits buy orders

No data loading. No execution logic.

```python
class EMAStrategy(fm.StrategyBase):
    def __init__(self, top_n, holding_period, stoploss, target):
        self.top_n = top_n
        self.holding_period = holding_period
        self.stop_loss = stoploss
        self.target = target

    def forward(self, data: fm.constants.MarketGraphData) -> List[fm.constants.Order]:
        # skip weekends
        if data.timestamp.weekday() in (5, 6):
            return []

        scored = []
        for symbol, sd in data.stocks.items():
            fast = sd.features["fast_avgs"]
            slow = sd.features["slow_avgs"]

            # bullish crossover
            if fast[0] < slow[0] and fast[1] > slow[1]:
                gap = fast[1] - slow[1]
                scored.append((symbol, sd, gap))

        scored.sort(key=lambda x: x[2], reverse=True)
        selected = scored[: self.top_n]

        orders = []
        value_frac = 1 / max(len(selected), 1)

        for symbol, sd, gap in selected:
            orders.append(
                fm.constants.Order(
                    timestamp=data.timestamp,
                    symbol=symbol,
                    price=sd.close,
                    order_type=fm.constants.ORDERTYPE.buy,
                    value_frac=value_frac,
                    stop_loss=sd.close * (1 - self.stop_loss),
                    target=sd.close * (1 + self.target),
                    hold_uptill=data.timestamp + dtm.timedelta(days=self.holding_period),
                    remarks=f"EMA gap={gap:.4f}",
                )
            )

        return orders
```

Key observations:

* No quantity computation
* No portfolio inspection
* Orders express **intent only**

Stragy should operate on `MarketGraphData`. You never pass raw OHLCV arrays directly to a strategy.


A strategy is a **pure function** from market state to order intent.

```python
class MyStrategy(StrategyBase):
    def forward(self, data: MarketGraphData):
        orders = []
        if some_signal(data):
            orders.append(
                Order(
                    timestamp=data.timestamp,
                    symbol="AAPL",
                    price=data.stocks["AAPL"].close,
                    order_type=ORDERTYPE.buy,
                    value_frac=0.1,
                )
            )
        return orders
```

Rules you must follow:

* return a list of `Order`
* do not inspect portfolio state
* do not compute quantities
* do not simulate execution

If you break these rules, backtests become meaningless.

## Step 3: Initialize Portfolio

The Portfolio tracks:

* cash
* positions
* open orders

You do **not** subclass Portfolio for most use cases.

The portfolio:

* accepts orders
* requests execution
* enforces accounting constraints


The portfolio initialization requires:-
- starting_cash -  keeping it to 100 for ease of calculations
- total_accounts - numbers of isolated accounts. Cash is devided equally amongst all accounts at first.
- [executioner](https://dev-ddr.github.io/finmetry/concepts/executioners/) - for added market noise. However, here it is not doing anyting.

```python
ortfolio = fm.Portfolio(starting_cash=100, total_accounts=stg1.total_accounts, executioner=fm.executioners.ExecutionModel())
```

## Step 4: Backtesting

The Backtester wires everything together.

```python
bt = Backtester(
    data_loader=data_loader,
    strategy=strategy,
    portfolio=portfolio,
)

bt.run()
```

What happens internally at each timestamp:

1. market snapshot is observed
2. strategy emits entry orders
3. portfolio emits exit orders
4. exit orders execute first
5. entry orders execute next
6. portfolio is marked to market

You never manually call these steps.

## Inspecting Results

After the run, all results live in the Portfolio:

* trade history
* equity curve
* drawdowns
* position timelines

Because Orders are preserved end‑to‑end, you can always trace **why** a trade happened.

---

## Live Trading (Later)

To go live, you replace only **one component**:

```text
ExecutionModel → LiveExecutionModel
```

Everything else stays the same:

* Strategy code
* Portfolio logic
* Order semantics


## Common Mistakes

Avoid these:

* sizing positions inside strategies
* reading portfolio state in strategies

---
---