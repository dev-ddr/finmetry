from importlib.metadata import version
__version__ = version("finmetry")


from . import clients
from .stocks_handler import Stock, StockDict
from . import constants