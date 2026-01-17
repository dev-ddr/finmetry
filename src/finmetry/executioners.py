from .constants import Order, FillEvent

from .constants import MarketGraphData

class ExecutionModel:
    def fill(self, order: Order, market: MarketGraphData) -> FillEvent:
        """
        Naive execution: fill immediately at order.price
        """
        return FillEvent(
            order=order,
            fill_price=order.price,
            qty=order.qty,
            timestamp=market.timestamp,
        )
