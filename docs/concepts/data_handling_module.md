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