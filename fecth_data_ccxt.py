
import pandas as pd
from numpy import timedelta64


import ccxt


exchange = ccxt.binance()


from_ts = exchange.parse8601('2023-05-01 00:00:00')
ohlcv_list = []
ohlcv = exchange.fetch_ohlcv('ETH/USDT', '5m', since=from_ts, limit=1000)
ohlcv_list.append(ohlcv)
while True:
    from_ts = ohlcv[-1][0]
    new_ohlcv = exchange.fetch_ohlcv('ETH/USDT', '1m', since=from_ts, limit=1000)
    ohlcv.extend(new_ohlcv)
    if len(new_ohlcv)!=1000:
    	break

print(len(ohlcv_list[0]))
df = pd.DataFrame(ohlcv_list[0], columns=['timestamp', 'open', 'high', 'low','close', 'volume'])

# df.head()
df['timestamp'] = pd.to_datetime(df['timestamp'], unit= 'ms') + timedelta64(7, 'h') # convert time to UTC+7

print('dd')