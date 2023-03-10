
import yfinance as _yf

import numpy as _np
import pandas as _pd
import datetime as _dtm
import os as _os


class yf_base:

    def __init__(self,symbol):
        self.tik = _yf.Ticker(symbol + '.NS')