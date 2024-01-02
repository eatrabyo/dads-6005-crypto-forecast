import requests
from time import sleep
from datetime import datetime as dt

# garbage collector
import gc
gc.enable()
gc.collect()

# get data 1m 5m 15m 1h 1d 
def get_data(symbol= 'ETHUSDT', tf= '1m'):
    symbol = symbol.upper()
    endpoint = f'https://api.binance.com/api/v3/ticker?symbol={symbol}&windowSize={tf}'
    res = requests.get(endpoint).json()
    res = {k: float(v) for k, v in res.items() if k != 'symbol'}
    
    return res
    
    
def append_to_file(row_data: str, symbol, window, base_path= './dataset/realtime/raw_'):
    if isinstance(row_data, dict):
        row_data = ','.join(str(value) for value in row_data.values())
        
    if row_data[-1] != '\n':
        row_data += '\n'
    path = base_path + f'{symbol.lower()}_{window}.csv'
    with open(path, 'a') as f:
        f.write(row_data)
    print(f'{dt.now().time()} append {symbol} data to {path}')
    return True



if __name__ == '__main__':
    import sys
    # print(f'RUNNING :{sys.argv[0]}')
    args = sys.argv
    symbol = args[1]
    window = args[2]
    print(f'Start get ticker :{symbol} window size :{window}')
    while True:
        try:
            res = get_data(symbol= symbol, tf= window)
            append_to_file(row_data= res, symbol= symbol, window= window)
            del res
        except Exception as e:
            print(e)
            pass
        sleep(1)


# dct = {'test': 'value1', 'key2': 'value2'}
# ','.join(str(value) for value in dct.values())
# str(dct)