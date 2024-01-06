import pandas as pd
from time import sleep
import matplotlib.pyplot as plt
from pandas import to_datetime
import matplotlib.dates as mdates
from pprint import pprint
import pickle
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler


from get_ticker import get_ohlc
from river_pipe import preprocessing_pipeline, MultiKeyShift
from river_pipe import learn_pred, create_metric,create_pipeline

# load offline model
rf = pickle.load(open('rf_pipe.pkl', 'rb'))
scaler = MinMaxScaler(feature_range=(0,1))

symbol = 'ETHUSDT'
metric_str = 'RMSE'
metric_rolling_size = 60
seed = None
data_key = ['openPrice', 'highPrice', 'lowPrice', 'lastPrice', 'priceChangePercent',
            'volume']
y_key = 'lastPrice'
window_size = 60


## INIT MULTISHEY SHIFT 

multi_key_shift = MultiKeyShift(keys= data_key, window_size= window_size, key_exclude= y_key)
## INIT PIPELINE
model_pl = create_pipeline(num_seed=seed)
## INIT METRIC
model_metric = create_metric(metric_rolling_size)

river_result = []
dct_result = {}

c = 0

while True: # use when get real data
    price_df,record = get_ohlc(symbol)
    # pprint(record)

    prep_rec = preprocessing_pipeline(record)
    data_ = {key: prep_rec[key] for key in data_key}
    data_['lastPrice'] = record['lastPrice']
    
    prep_rec = data_
    
    prep_rec = multi_key_shift.update(prep_rec)
    prep_rec = multi_key_shift.get()

    y = prep_rec.pop(y_key)

    
    ## LEARN AND PREDICT
    try:
        y, y_pred, model_pl, model_metric = learn_pred(x= prep_rec, y= y, pipeline= model_pl, metric= model_metric)
    except Exception as e:
        print(e)
        continue
    y_pred_rf = rf.predict(price_df.loc[:,['open','high', 'low', 'close', 'volume']])

    rmse_rf = mean_squared_error([y], y_pred_rf,squared=False)
    

    dct_result = {
        'closeTime': record['closeTime'],
        'y_actual_AMF': y,
        'y_predict_AMF': y_pred,
        f'{metric_str}_AMF': model_metric.get(),
        'y_predict_rf': y_pred_rf[0],
        f'{metric_str}_rf': rmse_rf,
    }
    
    if  y_pred != None:
        river_result.append(dct_result)
        print(dct_result)
    
    sleep(1)
    c+=1
    if c > window_size + 600:
        break

 
def plot_result():
    global window_size

    close_times = [to_datetime(result['closeTime'], unit='ms') for result in river_result]

    y_actual_values_AMF = [result['y_actual_AMF'] for result in river_result]
    y_predict_values_AMF = [result['y_predict_AMF'] for result in river_result]
    rmse_values_AMF = [result['RMSE_AMF'] for result in river_result]

    y_predict_values_rf = [result['y_predict_rf'] for result in river_result]
    rmse_values_rf = [result['RMSE_rf'] for result in river_result]

    # Plot the line graph with each second as a data point
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))

    # Plot actual and predicted values
    ax1.plot(close_times, y_actual_values_AMF, label='Actual', marker='o', linestyle='-', markersize=5, color='blue')  
    ax1.plot(close_times, y_predict_values_AMF, label='Predicted_AMF', marker='x', linestyle='-', markersize=5, color='green')  
    ax1.legend(loc='upper left')

    ax1.set_ylabel('Values', color='blue')
    ax1.set_title('Actual vs Predicted Values over Time')

    plt.xticks(rotation=30)

    ax1.ticklabel_format(style='plain' ,axis='y')
    
    # Plot actual and predict values
    ax2.plot(close_times, y_actual_values_AMF, label='Actual', marker='o', linestyle='-', markersize=5, color='blue')  
    ax2.plot(close_times, y_predict_values_rf, label='Predicted_rf', marker='x', linestyle='-', markersize=5, color='orange')  
    ax2.legend(loc='upper left')

    ax2.set_ylabel('Values', color='blue')
    ax2.set_title('Actual vs Predicted Values (Random Forest)')

    plt.xticks(rotation=30)
    
    ax3.plot(close_times, rmse_values_AMF, label='rmse_AMF', marker='o', linestyle='-', markersize=5, color='blue')  # Blue color for actual values
    ax3.plot(close_times, rmse_values_rf, label='rmse_rf', marker='x', linestyle='-', markersize=5, color='green')  # Green color for predicted values

    # Set labels and title for the first y-axis
    ax3.set_xlabel('Close Time')
    ax3.set_ylabel('RMSE Values', color='blue')
    ax3.set_title('RMSE')

    # Show legend for the first y-axis
    ax3.legend(loc='upper left')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=30)

    # Set the x-axis format to show date and time
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.tight_layout()

    # Show the plot
    plt.show()
        
plot_result()
