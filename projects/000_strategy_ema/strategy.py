from typing import List
import datetime as dtm

import finmetry as fm

LOCAL_DATA_FOLDPATH = "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/historical_data"

def get_ema_stock_data(stock:fm.Stock, timestamp:str, fast_window:int, slow_window:int, local_data_foldpath:str=LOCAL_DATA_FOLDPATH)->fm.StockData:

    end_time = fm.str_to_dtm(timestamp)
    start_time = end_time - dtm.timedelta(days=slow_window)
    d1 = stock.load_historical_data(start=start_time, end=end_time, interval=fm.constants.INTERVAL.one_day, local_data_foldpath=local_data_foldpath)

    slow_avg = d1['Close'].mean()

    start_time = end_time - dtm.timedelta(days=fast_window)
    d1 = stock.load_historical_data(start=start_time, end=end_time, interval=fm.constants.INTERVAL.one_day,local_data_foldpath=local_data_foldpath)

    fast_avg = d1['Close'].mean()
    last_data = d1.iloc[-1]
    return fm.StockData(
        symbol=stock.symbol,
        open=last_data["Open"],
        high=last_data["High"],
        low=last_data["Low"],
        close=last_data["Close"],
        volume=last_data["Volume"],
        timestamps=end_time,
        features={
            "slow_avg":slow_avg,
            "fast_avg":fast_avg,
        }
    )
    

def get_ema_market_data(sd1:fm.StockDict, timestamp:str, fast_window:int, slow_window:int)->fm.MarketGraphData:
    assert slow_window > fast_window, "slow_window must be greater than fast window"


    nodes = {}
    for stock in sd1:
        nodes[stock.symbol] = get_ema_stock_data(
            stock,
            timestamp=timestamp, 
            fast_window=fast_window, 
            slow_window=slow_window,
            )
    return fm.MarketGraphData(timestamp=fm.str_to_dtm(timestamp),stocks=nodes)



class EMI(fm.StrategyBase):
    def __init__(
        self,
        top_n: int,
        holding_period: int,
        stoploss: float,
        target: float,
        qty: int = 1,
    ):
        self.top_n = top_n
        self.holding_period = holding_period
        self.stop_loss = stoploss
        self.target = target
        self.qty = qty

    def forward(self, data: fm.MarketGraphData) -> List[fm.constants.Order]:
        scored = []

        # 1. Compute EMA gap for each stock
        for symbol, stock_data in data.stocks.items():
            feats = stock_data.features
            if feats is None:
                continue

            fast = feats.get("fast_avg")
            slow = feats.get("slow_avg")

            if fast is None or slow is None:
                continue

            gap = fast - slow
            scored.append((symbol, stock_data, gap))

        # 2. Sort by gap descending
        scored.sort(key=lambda x: x[2], reverse=True)

        # 3. Select top-N with positive gap
        selected = [x for x in scored if x[2] > 0][: self.top_n]

        orders: List[fm.constants.Order] = []

        # 4. Create buy orders
        for symbol, stock_data, gap in selected:
            order = fm.constants.Order(
                symbol=symbol,
                qty=self.qty,
                price=stock_data.close,
                Datetime=data.timestamp,
                order_type=fm.constants.ORDERTYPE.BUY,
                hold_uptill=data.timestamp + dtm.timedelta(days=self.holding_period),
                stop_loss=stock_data.close * (1 - self.stop_loss),
                target=stock_data.close * (1 + self.target),
                remarks=f"EMA gap={gap:.4f}",
            )
            orders.append(order)

        return orders

