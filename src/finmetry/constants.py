from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import TypedDict, Optional, get_type_hints, Dict, Tuple
import pandas as pd
import uuid
from datetime import datetime

import numpy as np

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

@dataclass
class Order:
    symbol: str
    qty: float
    price: float
    Datetime: pd.Timestamp
    order_type: ORDERTYPE
    target: Optional[float] = None
    stop_loss: Optional[float] = None
    remarks: Optional[str] = None
    id: Optional[str] = None
    hold_uptill: Optional[pd.Timestamp] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())


@dataclass(frozen=True, slots=True)
class StockData:
    """
    Strategy input data (TorchGeometric-style Data object).
    All arrays must be aligned on the last dimension. Here, the data could be only the last value or it could be the array of historical data. The timestamps must match those values as well.
    """
    symbol: str

    timestamps: np.ndarray  # np.datetime64[ns] or int64 epoch

    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray
    
    features: Optional[Dict[str, np.ndarray]] = None


@dataclass(frozen=True, slots=True)
class MarketGraphData:
    """
    Multi-asset market snapshot.
    """

    ### the time of the data. The StockData could have historical data upto this timestamp.
    timestamp: str|datetime|np.datetime64

    ### nodes, named after its symbol
    stocks: Dict[str, StockData]

    ### edges: (src, dst) → edge feature vector. from one node to other.
    edges: Optional[Dict[Tuple[str, str], np.ndarray]] = None

    ### optional global features (VIX, index returns, liquidity, etc.)
    global_features: Optional[Dict[str, np.ndarray]] = None


### Events

### the marketevent can be different for different strategy based on the data. So, if the strategy uses different samples of stocks then its data will be different and so its MarketEvent will be different even for the same timestamp.
@dataclass(frozen=True)
class MarketEvent:
    timestamp: str|datetime
    data: "MarketGraphData"


@dataclass(frozen=True)
class OrderEvent:
    order: Order


@dataclass(frozen=True)
class FillEvent:
    order: Order
    fill_price: float
    qty: float
    timestamp: datetime



@dataclass
class Position:
    symbol: str
    qty: float
    entry_price: float
    stop_loss: float | None
    target: float | None
    expiry: datetime | None
