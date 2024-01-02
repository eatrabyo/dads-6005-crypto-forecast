from pandas import to_datetime
from numpy import timedelta64

from river import stats , preprocessing
from river.compose import Pipeline, FuncTransformer
from river.linear_model import LinearRegression
from river.preprocessing import StandardScaler
from river import forest
from river.forest import ARFRegressor

from river.utils import Rolling
from river.metrics import MAE , RMSE

import requests
from time import sleep
from datetime import datetime as dt

############# Tricker ####################
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


############# DATA PREPROCESSING ####################
def convert_timestamp(dct, unit= 'ms'):
    dct['openTime'] = to_datetime(dct['openTime'], unit= unit) + timedelta64(7, 'h')
    dct['closeTime'] = to_datetime(dct['closeTime'], unit= unit) + timedelta64(7, 'h')
    return dct


def time_extractor(dct):
    dct['date'] = str(dct['closeTime'].date())
    dct['hour'] = dct['closeTime'].hour
    dct['min'] = dct['closeTime'].minute
    
    return dct

def convert_datatype(dct):
    base_dct = dct
    # dct = {key: float(dct[key]) for key in dct.keys() if 'Time' not in key and 'x'}
    dct = {key: float(dct[key]) if 'Time' not in key else dct[key] for key in dct.keys()}

    return dct


def preprocessing_pipeline(dct):
    dct = convert_timestamp(dct)
    dct = convert_datatype(dct)
    dct = time_extractor(dct)

    
    return dct
    
    
    

    
# EXCLUDE KEY
class MultiKeyShift:
    def __init__(self, keys, window_size, key_exclude= 'lastPrice'):
        self.key_exclude = key_exclude
        keys.remove(key_exclude)
        self.keys = keys
        self.shifts = {key: stats.Shift(window_size) for key in keys}


    def update(self, dct):
        self.dct_y = {self.key_exclude: dct[self.key_exclude]}
        dct_x = {key: self.shifts[key].update(dct[key]) for key in self.keys}
        return {**dct_x, **self.dct_y}
    
    def get(self):
        dct_x = {key: self.shifts[key].get() for key in self.keys}
        return {**dct_x, **self.dct_y}



############ MODEL ############
# def create_pipeline():
    
#     pl = Pipeline(
#         # ('ordinal_date', FuncTransformer(get_ordinal_date)),
#         ('scale', StandardScaler()),
#         ('AMF REG ', AMFRegressor(seed=42))
#         # ('lr', LinearRegression())
#     )
#     print(pl)

#     return pl

def create_pipeline():
    
    pl = Pipeline(
        ('ordinal_date', FuncTransformer(get_ordinal_date)),
        ('scale', preprocessing.StandardScaler()),
        ('lr', forest.ARFRegressor(seed=42))
    )
    print(pl)

    return pl

def create_metric():
    return Rolling(RMSE(), 12)

def learn_pred(x, y, pl, metric):
    
    # version 0.21.0
    if x['openPrice'] == None:
        return x, y, None, pl, metric
    try:
        y_pred_old = pl.predict_one(x)
        pl.learn_one(x, y)
        metric.update(y, y_pred_old)
    except:
        return x, y, None, pl, metric
    

    return x, y, y_pred_old, pl, metric

    
if __name__ == '__main__':
    print(__name__)
    