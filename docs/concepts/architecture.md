# Architecture

For algo-trading/ quant-trading, the first thing required is the **strategy**. To develop a strategy we will need to *evaluate* it and for that we will have to **backtest** it. Moreover, we need the **data** for all this. The finmetry library provides the backbone of the strategy development pipeline.

The finmetry library takes care of :-
- downloading the stocks data using the client API
- storing the data and retrieving from it efficiently
- backtesting the strategy
- generating the report of the backtest
