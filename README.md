# Finmetry

This project is developed primarily for my personal use. I am developing this to keep the documentation, architecture and pipeline consistent so that I can focus more on developing strategies instead of developing pipelines.

Visit [Finmetry](https://dev-ddr.github.io/finmetry/) guide for further steps.

# Overview

Finmetry majorly consists of 4 modules. Each module responsible for various aspects of the fin-quant pipeline.

## Data handling module

```mermaid

flowchart LR

dp[DataProviderClient]
dh[DataHandler]
db[(database <br> local storage)]

dp --market-data <br> OHLCV--> dh
dh --write--> db
db --read--> dh


```
## Stocks handling module

```mermaid

flowchart LR

st1[Stock] -->
sd1@{ shape: procs, label: "StockDict"}
dhm([Data handling <br> module])

sd1 --data for stock *i* from <br>*t1* to *t2* timestamp--> dhm
dhm --OHLCV dataframe--> sd1

```

## Strategy module

```mermaid

flowchart LR

sconfig[[StrategyConfig]] -->
stg1[Strategy]-->
orders@{ shape: docs, label: "Orders" }
stginput@{ shape: lean-r, label: "TimeStamp" } --> stg1

```

## Portfolio handler


```mermaid

flowchart LR

orders@{ shape: docs, label: "Orders" } --> 
iflv@{ shape: diamond, label: "is live market" } --yes--> od[Place order <br> through clients] -->
ph1[PortfolioHandler]
iflv --"no"--> ph1

```

## Backtester


```mermaid

flowchart LR

subgraph loop["Loop"]
    direction LR
    lex@{ shape: rect, label: "LoopExecuter" } -->
    ts@{ shape: lean-r, label: "TimeStamp" } -->
    stg([Strategy <br> module]) --> 
    orders@{ shape: docs, label: "Orders" } -->
    ptf([Portfolio <br> Handler]) --> lex
end

t1[Start time] --> loop
t2["End time"] --> loop
loop --"end of loop"--> report
```

# Diagram Tries

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


---
---


```mermaid

flowchart LR

subgraph DATA["DataHandler"]
    %% direction  LR
    dp[DataProvider]
    dh[DataHandler]
    db[(database)]

    dp --market-data <br> OHLCV--> dh
    dh --write--> db
    db --read--> dh
end

subgraph STOCK["Stocks"]
    %% direction LR
    st1[Stock]
    sd1@{ shape: procs, label: "StockDict"}

    st1 --> sd1
end

subgraph STRATEGY["Strategy"]
    %% direction LR
    sconfig[[StrategyConfig]]
    stg1[Strategy]

    sconfig --> stg1

end
orders@{ shape: lean-r, label: "Orders" }
stg1 --> orders
sd1 --> stg1

%% STOCK e1@--data for stock *i* from <br>*t1* to *t2* timestamp--> DATA
%% DATA e2@--OHLCV dataframe--> STOCK
%% e1@{ animate: True}
%% e2@{ animate: True}
st1 --data for stock *i* from <br>*t1* to *t2* timestamp--> dh
dh --OHLCV dataframe--> st1

```

