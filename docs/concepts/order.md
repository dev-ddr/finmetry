## Order – Core Contract Object (Concepts)

`Order` is the **central contract object** of the entire pipeline. Every major component either **produces**, **consumes**, or **mutates** an `Order`.

If `MarketGraphData` represents *what the market is*, an `Order` represents *what the system wants to do about it*.

> The Order is the only object that flows end‑to‑end through Strategy → Portfolio → Execution.


## What an Order Represents

An `Order` is **not** a trade and **not** a fill.

It is a **time‑stamped instruction with intent**, progressively enriched as it moves through the system.

Lifecycle view:

```text
Strategy        Portfolio        Executioner
  |                |                  |
  |  intent only   |  state-aware     |  reality-aware
  |--------------->|----------------->|----------------->
        Order            Order              Order
```

The same object instance evolves — no translation layers, no duplication.


## Field Categories (Very Important)

The `Order` fields are intentionally grouped by **ownership**.

### 1. Intent Fields (Strategy‑Owned)

These fields **must be set by the Strategy** and must never be modified by Execution.

* `timestamp` - origin time of intent
* `symbol` - stock symbol
* `price` - the price at which order is intended
* `order_type` - type of order: finmetry.ORDERTYPE (Enum)....right now only `buy` and `sell`
* `value_frac` - the fraction of capital to be utilized for this order. This is gross meaning including brokerage.
* `target` - the target price, if hit then exit
* `stop_loss` - the stop loss price, if hit then exit
* `hold_uptill` - the deadline upto which to hold the stock. its a timestamp
* `remarks` - any text remarks
* `account_idx` - this is to tell portfolio, in which account this order shall be placed. Strategy pre-determines the total number of accounts in portfolio.

These describe *what the strategy wants*, not what happens.


### 2. Identity & Tracking

* `id`

Every order is uniquely identifiable across:

* backtests
* logs
* execution traces
* live trading

Order IDs are generated at creation time and **never change**. The exit orders are mapped with the same id by portfolio to match the entry and exit order.


### 3. Execution‑Filled Fields (Executioner‑Owned)

These fields **must only be written by the ExecutionModel**.

* `fill_price`
* `fill_qty`
* `fill_timestamp`
* `brokerage_cost`
* `total_cost`
* `fill_remarks`

Before execution, these fields are `None` (or zero where applicable).

After execution, they define **what actually happened**.


## Why This Object Deserves Its Own Concept Doc

Because `Order` is:

* the **Strategy → Portfolio boundary**
* the **Portfolio → Execution boundary**
* the **single source of truth** for trades
* the object used for **PnL attribution, analytics, and debugging**

Any ambiguity here contaminates the entire system.

## Buy vs Sell Semantics

### Buy Orders

* `value_frac` defines capital allocation
* quantity is *derived* during execution
* cash constraint is enforced by Execution

### Sell Orders

* quantity is implied from existing position
* execution determines net receivable

Strategies never compute fill quantities.

## Multi‑Account Support

`account_idx` allows:

* multiple isolated capital pools
* parallel strategies
* realistic fund‑style simulations

The order always knows **which cash bucket it belongs to**.


## What an Order Must NOT Do

An `Order`:

* MUST NOT contain portfolio state
* MUST NOT simulate execution
* MUST NOT modify market data

It is a message — not a decision engine.

## Mental Model

Think of `Order` as a **typed message envelope**:

* Strategy writes the front of the envelope
* Execution stamps the back
* Portfolio files it permanently

Everything else revolves around it.

## Summary

* Order is the system’s core contract
* It separates intent from reality
* It evolves, but is never replaced

Without a well‑defined Order, the architecture collapses.
