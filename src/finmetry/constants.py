from enum import Enum


class EXCHANGE(Enum):
    nse = "N"
    bse = "B"
    mcx = "MCX"


class EXCHANGE_TYPE(Enum):
    cash = "C"
    derivative = "D"
    currency = "U"


class INTERVAL(Enum):
    one_day = "1d"
    one_min = "1m"
    five_min = "5m"
    fifteen_min = "15m"


class ORDERTYPE(Enum):
    buy = "buy"
    sell = "sell"
