
# Portfolio handler

This section explains how the **Portfolio**, **Account**, and **ExecutionModel** interact during a backtest. I have only impemented the *Portfolio* class with backtest in mind. I have not yet thought on how will this be used in live.

*Portfolio* consists of multiple *Acoounts*. These accounts are predetermined by strategy. It is the responsibility of the Strategy to tell the number of accounts and also the account index for each order. The job of *Portfolio* class is then to maintain the registry of past orders, current holdings, valuations etc. Also, the exit conditions (which is specified in the Order) are also checked by *Portfolio* class on each market data.


## High‑level Architecture


```mermaid
flowchart LR
    Market[MarketGraphData]
    Portfolio
    Account1[Account 0]
    Account2[Account 1]
    Executioner[ExecutionModel]

    Market -->|price updates| Portfolio
    Portfolio -->|mark_to_market| Account1
    Portfolio -->|mark_to_market| Account2

    Portfolio -->|on_order| Account1
    Portfolio -->|on_order| Account2

    Account1 -->|fill_order| Executioner
    Account2 -->|fill_order| Executioner
```

**Key idea**:
Portfolio is only a **coordinator**. All cash, holdings, and PnL logic live inside individual Accounts.


## Portfolio → Account Lifecycle

```mermaid
sequenceDiagram
participant M as Market
participant P as Portfolio
participant A as Account
participant E as ExecutionModel


M->>P: MarketGraphData(timestamp, prices)


%% Mark-to-market flow
P->>A: mark_to_market(market_data)
A->>A: update ltp for holdings
A->>P: AccountSnapshot(cash, holdings_value)


%% Exit check flow
P->>A: on_market(market_data)
A->>A: check stop_loss / target / expiry
A-->>P: exit_orders[]


%% Order execution flow
P->>A: on_order(order)
A->>E: fill_order(available_cash, order)
E-->>A: filled order
A->>A: update cash
A->>A: update holdings
```
Notes:

- on_market is a pure decision step: no cash or holdings mutation

- Exit orders reuse the original order_id, enforcing strict position pairing

- Actual state changes happen only in on_order

## Order Flow (Buy → Hold → Exit)

```mermaid
stateDiagram-v2
    [*] --> BuyOrder
    BuyOrder --> Holding: order filled

    Holding --> StopLossExit: price <= stop_loss
    Holding --> TargetExit: price >= target
    Holding --> ExpiryExit: holding_end_date reached

    StopLossExit --> [*]
    TargetExit --> [*]
    ExpiryExit --> [*]
```

Each holding is **keyed by order_id**, enforcing:

* No partial exits on the same order
* Clean buy → sell pairing


## Multi‑Account Isolation

```mermaid
flowchart TB
    Portfolio

    subgraph Account_0
        Cash0[Cash]
        Holdings0[Holdings]
        Orders0[Order Book]
    end

    subgraph Account_1
        Cash1[Cash]
        Holdings1[Holdings]
        Orders1[Order Book]
    end

    Portfolio --> Account_0
    Portfolio --> Account_1
```

**Invariant**:
Accounts never share cash, holdings, or orders. Portfolio aggregates **value only**, nothing else.


## Mark‑to‑Market Logic

```mermaid
flowchart LR
    MarketData -->|close price| Holding
    Holding -->|qty × ltp| HoldingsValue
    HoldingsValue --> AccountSnapshot
    AccountSnapshot --> PortfolioSnapshot
```

Portfolio value at time *t*:

```
Σ (account.cash + account.holdings_value)
```

## Design Guarantees

* **Deterministic accounting**: cash is updated immediately on fill
* **Strict position pairing**: buy & sell share the same `order_id`
* **Account‑level isolation**: enables parallel strategies
* **Portfolio‑level aggregation**: clean performance reporting

This structure intentionally avoids hidden state and cross‑account leakage.


---