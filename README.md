# Finmetry

This project is developed primarily for my personal use. I am developing this to keep the documentation, architecture and pipeline consistent so that I can focus more on developing strategies instead of developing pipelines.

Visit [Finmetry](https://dev-ddr.github.io/finmetry/) guide for further steps.

# Overview

Finmetry majorly consists of 5 modules. Each module responsible for various aspects of the fin-quant pipeline.



```mermaid

flowchart TB

subgraph DATA["Data handlers"]
    %% direction  LR
    dp[DataProviderClient]
    dh[DataHandler]
    db[(database <br> local storage)]

    dp --market-data <br> OHLCV--> dh
    dh --write--> db
    db --read--> dh
end

sd1@{ shape: procs, label: "StockDict"}

subgraph STRATEGY["Strategy"]
    %% direction LR
    sconfig[[StrategyConfig]]
    stg1[Strategy]
end

orders@{ shape: docs, label: "Orders" }
stginput@{ shape: lean-r, label: "TimeStamp" }
stg1 --> orders
sd1 --> stg1
stginput --> stg1

sd1 --data for stock *i* from <br>*t1* to *t2* timestamp--> dh
dh --OHLCV dataframe--> sd1

```

