import requests
from pprint import pprint
import pandas as pd
from numpy import timedelta64
from datetime import datetime

from db_connection import mydb_engine
from update_sql import insert_eth

"""
-- dads_6005.eth_price definition

CREATE TABLE `eth_price` (
  `datetime` datetime NOT NULL,
  `open` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `pct_chg` double DEFAULT NULL,
  `w_avg_price` double DEFAULT NULL,
  PRIMARY KEY (`datetime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

"""
ENGINE = mydb_engine
ticker = 'ETHUSDT'
request_url = f'https://api.binance.com/api/v3/ticker?symbol={ticker}'

limit_time = 60

df = pd.DataFrame()

start = datetime.now()
while True:
    data = requests.get(request_url).json()
    eth = pd.DataFrame([data])

    eth['openTime'] = pd.to_datetime(eth['openTime'],unit='ms') + timedelta64(7, 'h')
    eth['closeTime'] = pd.to_datetime(eth['closeTime'],unit='ms') + timedelta64(7, 'h')
    insert_eth(eth,ENGINE)
    stop = datetime.now()
    # df = pd.concat([df,eth])
    if ((stop - start).seconds % 3600) // 60 >= limit_time:
        break
print(df.columns)
print('dd')