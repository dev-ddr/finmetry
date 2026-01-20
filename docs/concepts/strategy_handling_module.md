

## Strategy module

You may think that this module would be the longest or the most important one. But surprisingly, this was the most easiest of all. I simply had to make few abstract classes to define the protocol. So, let's get on to that:-

```mermaid

flowchart LR

subgraph STG["Strategy Module"]
    stgdata[[StgData]] -->
    mgd["MarketGraphData"]
    config[[StrategyConfig]] -->
    stg1[StrategyBase]

    mgd --> stg1
end
sd1[StockDict] --> stgdata
stginput@{ shape: lean-r, label: "TimeStamp" }
orders@{ shape: docs, label: "Orders" }
stginput --> stgdata
stg1 --> orders

```

The core idea is that
> The strategy shall take in the market-data (mostly with computed features) and output the order.

So, let's first go to *data* part

## StgData:- Strategy related Data computation

I took motivation from [PyG](https://pytorch-geometric.readthedocs.io/en/latest/get_started/introduction.html) for structuring the data. I am assuming that the all the information required to any strategy can be represented as a *Graph*. The StgData is simply a protocol with `__getitem`, `__len__`, and `__iter__` methods. You have to implement them according to the need of your strategy.

The protocol dictates that, `__getitem__` must take `timestamp: str|datetime` as an input and should output `MarketGraphData`. **You should keep all your strategy feature computations inside this class.**

### MarketGraphData:- Data holder of the market

The market data for a given *timestamp* is structured as a *Graph*. The nodes in the *Graph* are individual *StockData* objects (coming to that in a minute), and the relation between any two stocks can be represented by a directed graph-edge. Moreover, there is also *global_features* which can hold market-level features.

```python
@dataclass(frozen=True, slots=True)
class MarketGraphData:
    ### the time of the data. The StockData could have historical data upto this timestamp.
    timestamp: datetime|np.datetime64
    ### nodes, named after its symbol
    stocks: Dict[str, StockData]
    ### edges: (src, dst) --> edge feature vector. from one node to other.
    edges: Optional[DiEdgeData] = None
    ### optional global features (VIX, index returns, liquidity, etc.)
    global_features: Optional[Dict[str, np.ndarray]] = None
```

### StockData:- Data holder for indiividual Stock

The data and features for individual stocks are stored in *StockData* object. It holds the OHLCV values for a given timestamps along with the features required for the strategy.

```python
@dataclass(frozen=True, slots=True)
class StockData:
    symbol: str
    ### market data entry
    timestamp: datetime | np.datetime64
    open: float
    high: float
    low: float
    close: float
    volume: float
    ### anything else you want
    features: Optional[Dict[str, np.ndarray]] = None
```

### DiEdgeData:- Stock-Stock relations

DiEdgeData holds the features of stock-stock relationship. Note that, this is the directed edge.

```python
@dataclass(frozen=True, slots=True)
class DiEdgeData:
    start_node_symbol: str
    end_node_symbol: str
    features: Optional[Dict[str, np.ndarray]] = None
```

## StrategyBase

I took motivation from [pytorch.nn.Module](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html) and designed the protocol for *StrategyBase*. This class only have one method `forward`, which only inputs`MArketGraphData` and outputs `List[Orders]`. You can design your strategy any how, but you must follow the rule for `forward` method to make your strategy compatible with backtesting pipeline of Finemtry.




