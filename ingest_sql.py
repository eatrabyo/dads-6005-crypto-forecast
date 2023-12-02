import ccxt
from pprint import pprint
import pandas as pd
from sqlalchemy import text
from numpy import timedelta64

from db_connection import mydb_engine
from update_sql import insert_eth

ENGINE = mydb_engine
exchange = ccxt.binance()

def get_data(symbol= 'ETHUSDT'):

    data = exchange.fetch_ticker(symbol= symbol)
    return data


while True:
    data = get_data()
    eth = pd.DataFrame([data['info']])
    eth['avg_price'] = data['average']

    eth['datetime'] = pd.to_datetime(data['datetime']) + timedelta64(7, 'h')
    
    insert_eth(eth,ENGINE)

print('dd')