from ..portfolio_handler import Portfolio
from ..executioners import ExecutionModel
from ..strategy_handler import StgDataLoader, StrategyBase
from ..constants import MarketEvent


class Backtester:
    def __init__(self, data_loader: StgDataLoader, strategy: StrategyBase, portfolio: Portfolio):
        self.data_loader = data_loader
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self):
        for market_data in self.data_loader:
            market_event = MarketEvent(timestamp=market_data.timestamp, data=market_data)

            entry_orders = self.strategy(market_event.data)
            exit_orders = self.portfolio.get_exit_orders(market_event.data)
            ### keeping exit_orders first to avoid cash going negative
            all_orders = exit_orders + entry_orders
            for order in all_orders:
                self.portfolio.on_order(order)
            self.portfolio.mark_to_market(market_event.data)
