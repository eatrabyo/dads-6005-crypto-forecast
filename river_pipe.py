from pandas import to_datetime
from numpy import timedelta64

from river import stats
from river.compose import Pipeline
from river.preprocessing import StandardScaler

from river.forest import AMFRegressor, ARFRegressor

from river.utils import Rolling
from river.metrics import RMSE
from river import forest

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
def create_pipeline(num_seed):

    pl = Pipeline(
        ('scale', StandardScaler()),
        ('AMF REG ', AMFRegressor(seed=num_seed))
    )

    return pl

def create_metric(rolling_size= 12):
    met = RMSE
    return Rolling(met(), rolling_size)

def learn_pred(x, y, pipeline, metric):

    if x['openPrice'] == None:
        return y, None, pipeline, metric
    try:
        y_pred_old = pipeline.predict_one(x)
        pipeline.learn_one(x, y)
        metric.update(y, y_pred_old)
    except:
        return y, None, pipeline, metric

    return y, y_pred_old, pipeline, metric

    
if __name__ == '__main__':
    print(__name__)

