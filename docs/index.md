# Finmetry

**This project is developed for my personal use.** I am developing this to keep the documentation, architecture and pipeline consistent so that I can focus more on developing strategies instead of developing pipelines.

```mermaid

flowchart TB

subgraph DATA["Data handling"]
    %% direction  LR
    s1[Stock]
    
    subgraph Download["Downloading data"]
    dp[Client API]
    dh[finmetry<br>Client]
    end

    subgraph LOCAL["Local data"]
    db[(database <br> local storage)]
    end
    s1 --request--> dh --request--> dp --data--> dh --data-->s1
    s1 --write-->db --read--> s1

end

s1 --> sd1@{ shape: procs, label: "StockDict"}

subgraph STRATEGY["Strategy"]
    %% direction LR
    sdata[StgDataLoader] -->
    mgdata[MarketGraphData] -->
    stg1[Strategy]
end

orders@{ shape: docs, label: "Orders" }
stginput@{ shape: lean-r, label: "TimeStamp" }
stg1 --> orders
sd1 --> sdata
stginput --> sdata

%% sd1 --data for stock *i* from <br>*t1* to *t2* timestamp--> dh
%% dh --OHLCV dataframe--> sd1

```


> This project is solely developed for my personal use. I am publishing this only to keep myself updated and to remove the headache of setting up the framework again and again.

---

**Finmetry is a research-first quantitative trading framework** designed to keep
strategy logic, execution logic, and accounting logic strictly separated.

It exists to eliminate repeated reinvention of trading pipelines, so you can
focus on **researching strategies**, not rebuilding infrastructure.


## What Finmetry Is (and Is Not)

Finmetry is:

- a framework for systematic trading research
- equally suited for backtesting and live trading
- opinionated by design
- built around explicit, auditable abstractions

Finmetry is **not**:

- a strategy library
- a signal generator
- a black-box trading system

If you want flexibility at the cost of correctness, this framework will feel restrictive.
That restriction is intentional.


## The Core Trading Loop

Every strategy in finmetry follows the same explicit loop:

```text
Market Data → Strategy → Orders → Portfolio → Execution → Accounting
````

Each stage is implemented as a **separate module** with strict responsibilities.

This guarantees that:

* strategies remain stateless
* execution assumptions are explicit
* accounting is consistent
* backtests can be trusted
* live trading reuses the same abstractions


## High-Level Architecture

```mermaid
flowchart LR
    Data[Market Data]
    Strategy[Strategy]
    Orders[Orders]
    Portfolio[Portfolio]
    Execution[Execution Model]
    Accounting[State & PnL]

    Data --> Strategy
    Strategy --> Orders
    Orders --> Portfolio
    Portfolio --> Execution
    Execution --> Portfolio
    Portfolio --> Accounting
```

## Major Modules

Finmetry is organized into the following conceptual modules:

### [Client Handling](https://dev-ddr.github.io/finmetry/concepts/client_handling_module/)

Handles interaction with external systems such as broker APIs and live data feeds.
Keeps the rest of the framework broker-agnostic.

### [Stocks](https://dev-ddr.github.io/finmetry/concepts/stocks_handling_module/)

Manages symbols, historical data, and OHLCV storage.
Acts as the foundation for all market data access.

### [Strategy](https://dev-ddr.github.io/finmetry/concepts/strategy_handling_module/)

Consumes immutable market snapshots and emits **order intent only**.
Strategies never manage cash, positions, or execution details.

### [Orders](https://dev-ddr.github.io/finmetry/concepts/order/)

Orders are the contract between strategy, portfolio, and execution.
They represent intent, not outcome.

### [Executioners](https://dev-ddr.github.io/finmetry/concepts/executioners/)

Simulate (or connect to) market reality:
slippage, brokerage, partial fills, or live execution.

### [Portfolio](https://dev-ddr.github.io/finmetry/concepts/portfolio_handling_module/)

The single source of truth for positions, cash, and PnL.
All state mutation happens here.

### [Backtesting](https://dev-ddr.github.io/finmetry/concepts/backtesting_handling_module/)

Pure orchestration.
Iterates over time and wires everything together without adding logic.

## Final Note

> I have built this for my personal use in mind.


