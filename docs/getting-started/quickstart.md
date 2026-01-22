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

## Step 1: Prepare Market Data

Download the data to local folder. Refer here for [downloading historical data](https://github.com/dev-ddr/finmetry/tree/base/projects/downloading_historical_data).

Next is you need to tell the stock universe in which this strategy will work, which is an ensamble of stocks. Like, if your strategy only works on single stock then your stock universe consists of single stock.

### Example: EMA Crossover Strategy

We will:

* compute fast/slow EMA features per stock
* expose them via a `StgDataLoader`
* implement a strategy that emits buy orders on crossover

---

### Stock‑level Feature Computation

All feature computation happens **outside** the strategy.

```python
from typing import Iterator, List
import datetime as dtm
import pandas as pd
import numpy as np
import finmetry as fm

LOCAL_DATA_FOLDPATH = "/path/to/historical_data"


def get_ema_stock_data(
    stock: fm.Stock,
    timestamp: str | dtm.datetime,
    fast_window: int,
    slow_window: int,
) -> fm.constants.StockData:
    if stock.hist_data0 is None:
        raise RuntimeError("Historical data not loaded")

    end_time = fm.str_to_dtm(timestamp) if isinstance(timestamp, str) else timestamp
    hist: pd.DataFrame = stock.hist_data0
    hist = hist.loc[hist.index <= end_time]

    slow_avg_prev = hist.shift(1).iloc[-slow_window:]["Close"].mean()
    slow_avg_curr = hist.iloc[-slow_window:]["Close"].mean()
    fast_avg_prev = hist.shift(1).iloc[-fast_window:]["Close"].mean()
    fast_avg_curr = hist.iloc[-fast_window:]["Close"].mean()

    last = hist.iloc[-1]

    return fm.constants.StockData(
        symbol=stock.symbol,
        timestamp=end_time,
        open=last["Open"],
        high=last["High"],
        low=last["Low"],
        close=last["Close"],
        volume=last["Volume"],
        features={
            "fast_avgs": np.array([fast_avg_prev, fast_avg_curr]),
            "slow_avgs": np.array([slow_avg_prev, slow_avg_curr]),
        },
    )
```

Key point:

> **Strategies never compute indicators. They only consume them.**

---

### Market‑level Snapshot Construction

```python
def get_ema_market_data(
    sd: fm.StockDict,
    timestamp: str,
    fast_window: int,
    slow_window: int,
) -> fm.constants.MarketGraphData:
    nodes = {}
    for stock in sd:
        nodes[stock.symbol] = get_ema_stock_data(
            stock,
            timestamp,
            fast_window,
            slow_window,
        )

    return fm.constants.MarketGraphData(
        timestamp=fm.str_to_dtm(timestamp),
        stocks=nodes,
    )
```

This produces a **read‑only market snapshot** for a single timestamp.

---

### DataLoader Implementation

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

    def __getitem__(self, ts):
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

This is the **only place** where data loading and feature computation happens.

---

## Step 2: Strategy — Turning Features into Orders

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

---

## Step 3: Wire Everything Together

All strategies operate on `MarketGraphData`. You never pass raw OHLCV arrays directly to a strategy.

You do this by implementing a `StgDataLoader`.

```python
class MyDataLoader(StgDataLoader):
    def __iter__(self):
        ...

    def __getitem__(self, timestamp):
        return MarketGraphData(...)
```

Responsibilities:

* load historical market data
* compute all features
* return **immutable snapshots**

No portfolio logic. No trading logic.

---

## Step 2: Write a Strategy

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

---

## Step 3: Initialize Portfolio

The Portfolio tracks:

* cash
* positions
* open orders
* realized / unrealized PnL

You do **not** subclass Portfolio for most use cases.

```python
portfolio = Portfolio(initial_cash=1_000_000)
```

The portfolio:

* accepts orders
* requests execution
* enforces accounting constraints

---

## Step 4: Choose an Execution Model

Execution models define **how orders are filled**.

The default model is deterministic and instant:

```python
execution = ExecutionModel(brokerage_perc=0.001)
```

You can later replace this with:

* slippage models
* volume‑limited models
* live broker adapters

Strategy and Portfolio code remain unchanged.

---

## Step 5: Run the Backtester

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

---

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

This is intentional.

---

## Common Beginner Mistakes

Avoid these:

* sizing positions inside strategies
* mutating `MarketGraphData`
* reading portfolio state in strategies
* adding slippage in Portfolio
* reordering backtest steps

If you feel tempted to do any of the above, revisit the Concepts pages.

---

## What to Read Next

* Strategy Concepts (again, carefully)
* Portfolio Concepts
* Executioner Concepts

Then start experimenting.

---

## Final Note

`finmetry` is **research‑first**.

If something feels restrictive, that restriction is probably intentional.

Correctness beats convenience.
