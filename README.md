# Finmetry

This project is developed primarily for my personal use. I am developing this to keep the documentation, architecture and pipeline consistent so that I can focus more on developing strategies instead of developing pipelines.

Visit [Finmetry](https://dev-ddr.github.io/finmetry/) guide for further steps.



```mermaid

flowchart BT

subgraph DATA["DataHandler"]
    direction  LR
    dp[DataProvider]
    dh[DataHandler]
    db[(database)]

    dp --market-data <br> OHLCV--> dh
    dh --write--> db
    db --read--> dh
end

subgraph STOCK["Stocks"]
    direction LR
    st1[Stock]
    sd1@{ shape: procs, label: "StockDict"}

    st1 --> sd1
end

STOCK --data for stock *i* from <br>*t1* to *t2* timestamp--> DATA
DATA --OHLCV dataframe--> STOCK

```