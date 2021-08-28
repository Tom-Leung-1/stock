import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import sys
import random
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, datetime, timedelta, time
import statsmodels.api as sm
import statsmodels.graphics as gp
key = open('./config/key.txt').read()

def time_slice(x, y):
    pass


def mean_and_variance(df_list, col="open"):
    df_list2 = []
    for df in df_list:
        df_params = []
        df_params.append(df)
        params_dict = {}
        params_dict[col + '_sample_mean'] = df[col].mean()
        params_dict[col + '_sample_variance'] = df.var()[col]
        params_dict[col + 'max'] = df[col].max()
        params_dict[col + 'min'] = df[col].min()
        params_dict[col + 'change'] = params_dict[col + 'max'] -params_dict[col + 'min']
        params_dict[col + 'percent'] = params_dict[col + 'change'] / params_dict[col + 'min']
        df_params.append(params_dict)
        df_list2.append(df_params)
    return df_list2



def get_sample_mean(data_list):
    return sum(data_list)/len(data_list)

def get_sample_variance(data_list):
    mean = get_sample_mean(data_list)
    sample = [(x - mean) ** 2 for x in data_list]
    return sum([(x - mean)**2 for x in data_list]) / (len(data_list)-1)

def acf_analysis(x, date):
    acf = sm.tsa.stattools.acf(x)
    gp.tsaplots.plot_acf(x, title=date + " acf")
    return acf

def pacf_analysis(x, date):
    pacf = sm.tsa.stattools.pacf(x)
    gp.tsaplots.plot_pacf(x, title=date + " pacf")
    return pacf

def days_analysis(day_df_list, field):
    for idx, day in enumerate(day_df_list):
        x = np.array(day_df_list[idx][0][field])
        date = str(day_df_list[idx][0]['date'].iloc[0])
        x = remove_trend_and_variation(x)
        # acf_analysis(x, date)
        # pacf_analysis(x, date)
# Press the green button in the gutter to run the script.

def remove_trend_and_variation(x, var=True, diff=True):
    if var:
        log_x = np.log(x)
        # plt.plot(log_x)
    if diff and var:
        log_return_x = sm.tsa.statespace.tools.diff(log_x)
        plt.plot(log_return_x)
        return log_return_x
    else:
        diff_x = sm.tsa.statespace.tools.diff(x)
        plt.plot(diff_x)
        return diff_x

