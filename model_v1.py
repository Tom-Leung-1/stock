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

# failure: daytrading etf using this model wont work, need modification
class trading_model:
    # simple model:
    # based on open price, if price drops 0.004 -> buy all. if price rise 0.004 -> sell all (wait for next day) (limit order)
    # it fails!
    def __init__(self, principal, low_percent, high_percent, day_df_list):
        self.principal = principal
        self.low_percent = low_percent
        self.high_percent = high_percent
        self.acc_return = 1
        self.amount = principal
        self.day_df_list = day_df_list
        self.buy_price = 0
        self.sell_price = 0
        self.success_trade = 0
        self.close_exit = 0

    def buy(self):
        pass

    def sell(self):
        pass

    def day_trade(self):
        for df in self.day_df_list:
            df = df.reset_index(drop=True)
            open_price = df.iloc[0]['open']
            buy_price = open_price * (1 - self.low_percent) # limit order
            sell_price = open_price * (1 + self.high_percent)
            buy_df = df[df['open'] <= buy_price]
            if (len(buy_df.index)): # buy the stock. Exit before close
                buy_df = buy_df.reset_index(drop=True)
                buy_time = buy_df.iloc[0]['time']
                sell_df = df.loc[df['time'] >= buy_time]
                perfect_sell_df = sell_df[sell_df['open'] >= sell_price]
                if (len(perfect_sell_df.index)):
                    self.success_trade += 1
                    gain_loss = (sell_price - buy_price) / buy_price
                    self.acc_return *= (1 + gain_loss)
                    print("success: gain = ", gain_loss, " and acc_return = ", self.acc_return)
                else:
                    sell_idx = find_idx(sell_df, time(15, 30))
                    exit_price = sell_df.loc[sell_idx]['open'] # not accurate but approximate result
                    gain_loss = (exit_price - buy_price) / buy_price
                    self.acc_return *= (1 + gain_loss)
                    print("exit: gain/loss =", gain_loss, " and acc_return =", self.acc_return)






def find_idx(df, open_time):
    while True:
        day_idx_list = df.index[df['time'] == open_time].tolist()
        if (not len(day_idx_list)):
            dt = datetime.combine(date.today(), open_time) + timedelta(minutes=1)
            open_time = dt.time()
        else:
            return day_idx_list[0]

def plot_graph(x, y, title=None):
    plt.plot(x, y)
    plt.title(title)
    plt.show()

def get_data(ticker, get_all=False, interval="1min"):
    df = None
    if get_all:
        ts = TimeSeries(key=key, output_format='csv')
        data = ts.get_intraday_extended(symbol=ticker, interval=interval, slice='year1month2')
        data_list = list(data[0])
        df = pd.DataFrame(data_list[1:], columns=data_list[0])
        header_list = ['open', 'high', 'low', 'close', 'volume']
        for h in header_list:
            df[h] = df[h].astype(float)
        df['time'] = df.apply(lambda row: datetime.strptime(row.time, "%Y-%m-%d %H:%M:%S"), axis=1)
    else:
        ts = TimeSeries(key=key, output_format='pandas')
        data = ts.get_intraday(symbol=ticker, interval=interval, outputsize="full")
        df = pd.DataFrame(data[0])
        df["time"] = df.index
        df = df.rename(columns={x:x.split()[-1] for x in df.columns})
    df = df[::-1]
    df['date'] = df.apply(lambda row: row.time.date(), axis=1)
    df['time'] = df.apply(lambda row: row.time.time(), axis=1)
    return df

def get_day_result(df):
    start_day = df.iloc[0].at['date']
    end_day = df.iloc[-1].at['date']
    day_df_list =[]
    while start_day <= end_day:
        day_df = df.loc[df['date'] == start_day]
        start_day += timedelta(days=1)
        if day_df.empty:
            continue
        day_df_list.append(day_df)
    return day_df_list

def plot_graphs(day_df_list, col="open"):
    for df in day_df_list:
        title = str(df.iloc[0].at['date'])
        times = [datetime.strptime(str(h), "%H").time() for h in range(3,21)]
        df.plot(x ='time', y='open', kind='line', title=title, xticks=times, rot=45)
        plt.axvline(x=datetime.strptime("1990-01-01 09:30:00", "%Y-%m-%d %H:%M:%S").time(), c="black")
        plt.show()

def avg_percent(percent_lists, attr):
    average = sum(percent_lists) / len(percent_lists)
    print("average " + attr + ": ", average)

def min_percent(percent_lists, attr):
    min_percent = min(percent_lists)
    print("min " + attr + ": ", min_percent)

def max_percent(percent_lists, attr):
    max_percent = max(percent_lists)
    print("max " + attr + ": ", max_percent)

def open_attr_diff(day_df_list, open_time, attribute):
    attr_open_percents = []
    day_idx = None
    for day in day_df_list:
        day_idx = find_idx(day, open_time)
        day["open_" + attribute + "_diff"] = day.loc[day_idx]['open'] - day[attribute].min()
        attr_open_percents.append(day.iloc[0]["open_" + attribute + "_diff"] / day.loc[day_idx]['open'] * 100)
    return day_df_list, attr_open_percents

def time_range(open_time, close_time, day_df_list):
    df_list = []
    for df in day_df_list:
        df_list.append(df.loc[(df['time'] >= open_time) & (df['time'] <= close_time)])
    return df_list

if __name__ == '__main__':
    # ticker = input("ticker name: ") # ETF: DIA, SPY, QQQ
    tickers = ["DIA", "SPY", "QQQ"]
    for ticker in tickers:
        print("---------------------------------" "\n" + ticker)
        data = get_data(ticker, get_all=True)
        day_df_list = get_day_result(data)
        plot_graphs(day_df_list)
        day_df_list, low_open_percents = open_attr_diff(day_df_list, time(9, 30), 'low')
        day_df_list, high_open_percents = open_attr_diff(day_df_list, time(9, 30), 'high')
        avg_percent(low_open_percents, "low")
        avg_percent(high_open_percents, "high")
        min_percent(low_open_percents, "low")
        max_percent(low_open_percents, "low")
        min_percent(high_open_percents, "high")
        max_percent(high_open_percents, "high")
        # backtest
        day_df_list = time_range(time(9, 30), time(16, 0), day_df_list)
        model = trading_model(20000, 0, 0.002, day_df_list)
        model.day_trade()


    # day_df_list = mean_and_variance(day_df_list)
    # days_analysis(day_df_list, 'open')
    # acf = acf_analysis(day_df_list, 0, 'open')
    # pacf = pacf_analysis(day_df_list, 0, 'open')
    # sm.tsa.stattools.acf(np.array(day_df_list[0][0]['open']))
    # x, y = get_x_y(day_result[0])
    # plot_many_graphs(day_result)
    # sample_variance = get_sample_variance(y)
    # sample_mean = get_sample_mean(y)
    # days_list, variance_list = params_time_series(day_result, params="variance")
    # plot_graph(days_list, variance_list)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
