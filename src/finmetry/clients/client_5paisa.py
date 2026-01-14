"""
This module contains the objects related to 5paisa client

@author: Rathod Darshan
"""

import py5paisa as p5
import pandas as pd
import datetime as dtm
from typing import Union, TypedDict

from ..stocks_handler import Stock

from ..constants import INTERVAL

    

class ScripMaster:
    """ScripMaster contains all the scipts of 5paisa client.

    To get the name and symbol of any script, this class needs to be accessed. This class just filters the data from single .csv.
    """

    def __init__(self, filepath: str = None) -> None:
        """Initializes the ScripMaster class.

        Loads the .csv file into data attribute.

        Parameters
        ----------
        filepath : str, optional
            filepath to .csv file. If filepath is given then it reads the file, else it will download the file. by default None
        """
        if filepath is not None:
            self.data = pd.read_pickle(filepath)
        else:
            self.data = pd.read_csv("https://images.5paisa.com/website/scripmaster-csv-format.csv")

        self.data["Expiry"] = pd.to_datetime(self.data["Expiry"], format="%Y-%m-%d %H:%M:%S")
        self.data["Name"] = self.data["Name"].apply(str.upper)
        self.data["Symbol"] = self.data["Name"]

    def __repr__(self):
        return f"scrip master data"

    def __call__(self):
        return self.data

    def save(self, filepath: str) -> None:
        """saves the scrip master data

        Parameters
        ----------
        filepath : str
            filepath with filename with .pkl extention

        Returns
        -------
        _type_
            None
        """
        return self.data.to_pickle(filepath)

    def get_scrip(self, stock: Stock) -> pd.DataFrame:
        """returns the scrips of the stock

        Parameters
        ----------
        stock : Stock
            a stock object

        Returns
        -------
        pd.DataFrame
            Scrip data of a given stock
        """
        d1 = self.data
        f1 = (d1["Exch"] == stock.exchange) & (d1["ExchType"] == stock.exchange_type) & (d1["Symbol"] == stock.symbol)
        f2 = (d1["Series"] == "EQ") | (d1["Series"] == "XX")
        d2 = d1[f1 & f2]
        if d2.empty:
            raise ValueError(f"No Scrip found for {stock.symbol} in scrip_master")
        d2 = d2.set_index("Name")
        return d2



class Client5paisaCred(TypedDict):
    APP_NAME: str
    APP_SOURCE: str
    USER_ID: str
    PASSWORD: str
    USER_KEY: str
    ENCRYPTION_KEY: str

class Client5paisa(p5.FivePaisaClient):
    
    def __init__(self, totp:str, mpin:str, client_code:str, cred: Client5paisaCred, scrip_master:ScripMaster=None, **kwargs):
        super().__init__(cred=cred)
        self.get_totp_session(client_code,f'{totp}',mpin)

        print('downloading the scrip-master')

        self.scrip_master=ScripMaster() if scrip_master is None else scrip_master
        return
    
    def download_historical_data(
        self,
        stock: Stock,
        interval: INTERVAL = INTERVAL.one_day,
        start: Union[str, dtm.datetime] = "2023-01-01",
        end: Union[str, dtm.datetime] = "2023-03-30",
    ) -> pd.DataFrame:
        """Downloads the historical data and saves it to local drive or in Stock.data variable.

        Parameters
        ----------
        stock : Stock
            Stock object
        interval : str, optional
            time interval of data. it should be within [1m,5m,10m,15m,30m,60m,1d], by default "1d"
        start : Union[str, dtm.datetime], optional
            start date of the data. The data for this date will be downloaded, by default "2023-01-01"
        end : Union[str, dtm.datetime], optional
            end date of the data. The data for this date will be downloaded, by default "2023-03-30"
        
        Returns
        ----------
        pd.DataFrame
            A dataframe containing a historical data.
        
        """
        scrip = self.scrip_master.get_scrip(stock)

        if isinstance(start, dtm.datetime):
            start = start.strftime("%Y-%m-%d")
        if isinstance(end, dtm.datetime):
            end = end.strftime("%Y-%m-%d")

        df = self.historical_data(stock.exchange, stock.exchange_type, scrip.loc[stock.symbol, "Scripcode"], interval.value, start, end)
        df.columns = ["Datetime", "Open", "High", "Low", "Close", "Volume"]
        df["Datetime"] = pd.to_datetime(df["Datetime"])
        df = df.set_index("Datetime")

        return df



