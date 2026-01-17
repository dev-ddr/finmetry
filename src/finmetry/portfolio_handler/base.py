from typing import Dict, List

from ..constants import FillEvent, Order, MarketGraphData, Position, ORDERTYPE


class Portfolio:
    def __init__(self, starting_cash: float):
        self.cash = starting_cash
        self.positions: Dict[str, Position] = {}
        self.history: List[dict] = []

    def on_fill(self, fill: FillEvent):
        order = fill.order
        cost = fill.qty * fill.fill_price

        if order.order_type.name.lower() == "buy":
            self.cash -= cost
            self.positions[order.symbol] = Position(
                symbol=order.symbol,
                qty=fill.qty,
                entry_price=fill.fill_price,
                stop_loss=order.stop_loss,
                target=order.target,
                expiry=order.hold_uptill,
            )

        elif order.order_type.name.lower() == "sell":
            self.cash += cost
            self.positions.pop(order.symbol, None)

    def on_market(self, market: MarketGraphData) -> List[Order]:
        """
        Check stops, targets, expiry.
        Emits exit Orders if needed.
        """
        exit_orders: List[Order] = []

        for pos in list(self.positions.values()):
            price = market.stocks[pos.symbol].close

            reason = None
            if pos.stop_loss and price <= pos.stop_loss:
                reason = "stop_loss"
                exit_price = pos.stop_loss
            elif pos.target and price >= pos.target:
                reason = "target"
                exit_price = pos.target
            elif pos.expiry and market.timestamp >= pos.expiry:
                reason = "expiry"
                exit_price = price
            else:
                continue

            exit_orders.append(
                Order(
                    symbol=pos.symbol,
                    qty=pos.qty,
                    price=exit_price,
                    Datetime=market.timestamp,
                    order_type=ORDERTYPE.sell,
                    remarks=reason,
                )
            )

        return exit_orders
