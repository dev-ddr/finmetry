from .constants import Order, FillEvent

from .constants import MarketGraphData

class ExecutionModel:
    """ExecutionModel is a simulator of a real market. Slippage, volume limits, liquidity etc. kind of real-market scenarios should be implemented here. This could have also been done in portfolio handler but we apply it here for separating the responsibilities.

    Thus ExecutionModel introduces real-market noise. And portfolio simply stores the order.
    """
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
