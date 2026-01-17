
from ..portfolio_handler import Portfolio
from ..executioners import ExecutionModel

from ..constants import MarketEvent


class Backtester:
    def __init__(
        self,
        data_loader,
        strategy,
        portfolio: Portfolio,
        execution_model: ExecutionModel,
    ):
        self.data_loader = data_loader
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution = execution_model

    def run(self):
        for market_data in self.data_loader:
            market_event = MarketEvent(
                timestamp=market_data.timestamp,
                data=market_data,
            )

            # 1. Strategy generates entry orders
            entry_orders = self.strategy(market_event.data)

            # 2. Portfolio generates exit orders
            exit_orders = self.portfolio.on_market(market_event.data)

            # 3. Execute all orders
            for order in entry_orders + exit_orders:
                fill = self.execution.fill(order, market_event.data)
                self.portfolio.on_fill(fill)

            # 4. Record equity snapshot
            self._mark_to_market(market_event)

    def _mark_to_market(self, market_event: MarketEvent):
        equity = self.portfolio.cash
        for pos in self.portfolio.positions.values():
            equity += market_event.data.stocks[pos.symbol].close * pos.qty

        self.portfolio.history.append(
            {
                "timestamp": market_event.timestamp,
                "equity": equity,
                "cash": self.portfolio.cash,
            }
        )
