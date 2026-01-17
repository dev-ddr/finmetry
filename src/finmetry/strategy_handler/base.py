from abc import ABC, abstractmethod
from typing import List

from ..constants import Order

from ..constants import MarketGraphData, StockData


class StgDataHandler:

    def __get__(self):

        return


class StrategyBase(ABC):

    def __call__(self, data: MarketGraphData) -> List[Order]:
        orders = self.forward(data)

        if not isinstance(orders, list):
            raise TypeError("Strategy.forward must return List[Order]")

        return orders

    @abstractmethod
    def forward(self, data: MarketGraphData) -> List[Order]:
        raise NotImplementedError
