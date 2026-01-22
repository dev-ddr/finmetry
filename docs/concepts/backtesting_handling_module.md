
## Backtester – Concepts

The Backtester is the **orchestrator** of the entire system. It does not contain trading logic, feature logic, or execution logic. Its sole responsibility is to **coordinate the interaction** between data, strategy, portfolio, and execution in a strictly ordered loop.

> The backtester defines *when* things happen, never *how* they happen.


## Core Responsibility

At every timestamp, the backtester enforces the following invariant order:

1. Observe market state
2. Ask strategy for new orders
3. Ask portfolio for exit orders
4. Execute orders
5. Mark portfolio to market

No step is optional. No step is reordered.



## High-level Control Flow

```mermaid
flowchart LR
    DL[StgDataLoader] --> MGD[MarketGraphData]
    MGD --> STG[Strategy]
    MGD --> PF[Portfolio]

    STG --> EO[Entry Orders]
    PF --> XO[Exit Orders]

    XO --> ORD[Order Queue]
    EO --> ORD

    ORD --> PF
    PF --> MTM[Mark to Market]
```



## Event-driven View

```mermaid
sequenceDiagram
    participant D as StgDataLoader
    participant B as Backtester
    participant S as Strategy
    participant P as Portfolio
    participant E as ExecutionModel

    D->>B: MarketGraphData(t)
    B->>S: forward(MarketGraphData)
    S-->>B: entry_orders

    B->>P: get_exit_orders(MarketGraphData)
    P-->>B: exit_orders

    B->>P: on_order(exit_orders)
    P->>E: fill_order(...)
    E-->>P: filled exits

    B->>P: on_order(entry_orders)
    P->>E: fill_order(...)
    E-->>P: filled entries

    B->>P: mark_to_market(MarketGraphData)
```



## Ordering Guarantees (Critical)

### Exit Orders Before Entry Orders

Exit orders are **always executed before** new entry orders:

```python
all_orders = exit_orders + entry_orders
```

This guarantees:

* cash from exits is available for new entries
* no artificial `NegativeCashError`
* deterministic capital reuse

This is a **design rule**, not an optimization.



## What the Backtester Does NOT Do

The Backtester deliberately avoids:

* feature computation
* trading decisions
* order sizing
* execution modeling
* portfolio accounting

All such logic is delegated to specialized modules.



## Determinism & Reproducibility

Given:

* a deterministic `StgDataLoader`
* a deterministic `Strategy`
* a deterministic `ExecutionModel`

The backtest result is **fully reproducible**.

The Backtester itself introduces **no randomness**.

## Mental Model

Think of the Backtester as a **clock-driven state machine**:

* Time advances via `StgDataLoader`
* Decisions come from `Strategy`
* State lives in `Portfolio`
* Reality is simulated by `ExecutionModel`

The backtester only keeps time moving.



## Summary

* Backtester is a coordinator, not a logic holder
* Enforces strict ordering per timestamp
* Guarantees exit-before-entry execution
* Preserves determinism and replayability

This separation is intentional and foundational to the system.

