import pandas as pd
import requests
from numpy import timedelta64


def get_ohlc(ticker):

    request_url = f'https://api.binance.com/api/v3/ticker?symbol={ticker}&windowSize=1m'
    df = pd.DataFrame()

    data = requests.get(request_url).json()
    ohlc_df = pd.DataFrame([data])

    ohlc_df['openTime'] = pd.to_datetime(ohlc_df['openTime'],unit='ms') + timedelta64(7, 'h')
    ohlc_df['closeTime'] = pd.to_datetime(ohlc_df['closeTime'],unit='ms') + timedelta64(7, 'h')

    res = {k: float(v) for k,v in data.items() if k != 'symbol'}
    df = pd.concat([df,ohlc_df])
    df.rename(columns={'openPrice':'open',
               'highPrice':'high', 
               'lowPrice':'low', 
               'lastPrice':'close'},inplace=True)
    return df,res