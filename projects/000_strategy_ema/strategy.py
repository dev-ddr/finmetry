from typing import List, Iterator
import datetime as dtm
import pandas as pd
import numpy as np

import finmetry as fm

LOCAL_DATA_FOLDPATH = "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/historical_data"


def get_ema_stock_data(
    stock: fm.Stock,
    timestamp: str | dtm.datetime,
    fast_window: int,
    slow_window: int,
) -> fm.constants.StockData:
    if stock.hist_data0 is None:
        raise RuntimeError("stock.hist_data0 is not loaded")

    end_time = fm.str_to_dtm(timestamp) if isinstance(timestamp, str) else timestamp

    hist: pd.DataFrame = stock.hist_data0
    f1 = hist.index <= end_time
    hist = hist.loc[f1]

    slow_avg1 = hist.shift(1).iloc[-slow_window:]["Close"].mean()
    slow_avg2 = hist.iloc[-slow_window:]["Close"].mean()
    fast_avg1 = hist.shift(1).iloc[-fast_window:]["Close"].mean()
    fast_avg2 = hist.iloc[-fast_window:]["Close"].mean()

    last_data = hist.iloc[-1]

    return fm.constants.StockData(
        symbol=stock.symbol,
        open=last_data["Open"],
        high=last_data["High"],
        low=last_data["Low"],
        close=last_data["Close"],
        volume=last_data["Volume"],
        timestamp=end_time,
        features={
            "slow_avgs": np.array([slow_avg1, slow_avg2]),
            "fast_avgs": np.array([fast_avg1, fast_avg2]),
        },
    )


def get_ema_market_data(sd1: fm.StockDict, timestamp: str, fast_window: int, slow_window: int) -> fm.constants.MarketGraphData:
    assert slow_window > fast_window, "slow_window must be greater than fast window"

    nodes = {}
    for stock in sd1:
        nodes[stock.symbol] = get_ema_stock_data(
            stock,
            timestamp=timestamp,
            fast_window=fast_window,
            slow_window=slow_window,
        )
    return fm.constants.MarketGraphData(timestamp=fm.str_to_dtm(timestamp), stocks=nodes)


class EMIDataLoader(fm.StgDataLoader):
    def __init__(self, stockdict: fm.StockDict, start_date: str, end_date: str, fast_window: int, slow_window: int, local_data_foldpath: str = LOCAL_DATA_FOLDPATH):
        self.stockdict = stockdict
        self.start_date = fm.str_to_dtm(start_date)
        self.end_date = fm.str_to_dtm(end_date)
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.local_data_foldpath = local_data_foldpath

        self._shifted_start_date = self.start_date - dtm.timedelta(days=slow_window + 2)
        self.stockdict.load_historical_data(start=self._shifted_start_date, end=self.end_date, interval=fm.constants.INTERVAL.one_day, local_data_foldpath=self.local_data_foldpath, remove_error_stocks=True)

        self._all_timestemps = self.stockdict[0].hist_data0.index
        for stock in self.stockdict:
            idx = stock.hist_data0.index
            if len(idx) > len(self._all_timestemps):
                self._all_timestemps = idx
        f1 = self._all_timestemps >= self.start_date
        self._all_timestemps = self._all_timestemps[f1].date

    def __getitem__(self, idx: str) -> fm.constants.MarketGraphData:
        return get_ema_market_data(sd1=self.stockdict, timestamp=idx, fast_window=self.fast_window, slow_window=self.slow_window)

    def __len__(self):
        return len(self._all_timestemps)

    def __iter__(self) -> Iterator[fm.constants.MarketGraphData]:
        for ts in self._all_timestemps:
            yield self[str(ts)]


class EMI(fm.StrategyBase):
    def __init__(
        self,
        top_n: int,
        holding_period: int,
        stoploss: float,
        target: float,
    ):
        self.top_n = top_n
        self.holding_period = holding_period
        self.stop_loss = stoploss
        self.target = target
        self.total_accounts = 5

    def forward(self, data: fm.constants.MarketGraphData) -> List[fm.constants.Order]:
        ### skipping if the weekday is saturday or sunday
        if data.timestamp.weekday() in [5, 6]:
            return []

        scored = []
        # 1. Compute EMA gap for each stock
        for symbol, stock_data in data.stocks.items():
            feats = stock_data.features
            
            fast = feats.get("fast_avgs")
            slow = feats.get("slow_avgs")

            delta = fast - slow
            crossover = delta[0] < 0 and delta[1] > 0
            if not crossover:
                continue
            gap = delta[1]
            scored.append((symbol, stock_data, gap))

        # 2. Sort by gap descending
        scored.sort(key=lambda x: x[2], reverse=True)

        # 3. Select top-N with positive gap
        selected = [x for x in scored if x[2] > 0][: self.top_n]

        orders: List[fm.constants.Order] = []
        value_frac = 1 / self.top_n
        # 4. Create buy orders
        for symbol, stock_data, gap in selected:
            order = fm.constants.Order(
                symbol=symbol,
                value_frac=value_frac,
                price=stock_data.close,
                timestamp=data.timestamp,
                order_type=fm.constants.ORDERTYPE.buy,
                hold_uptill=data.timestamp + dtm.timedelta(days=self.holding_period),
                stop_loss=stock_data.close * (1 - self.stop_loss),
                target=stock_data.close * (1 + self.target),
                remarks=f"EMA gap={gap:.4f}",
                account_idx=data.timestamp.weekday(),
            )
            orders.append(order)

        return orders
