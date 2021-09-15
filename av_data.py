import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
key = open('./config/key.txt').read()
from datetime import date, datetime, timedelta, time


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

if __name__ == '__main__':
    # ticker = input("ticker name: ") # ETF: DIA, SPY, QQQ
    tickers = ["DIA", "SPY", "QQQ"]
    for ticker in tickers:
        print("---------------------------------" "\n" + ticker)
        data = get_data(ticker, get_all=True)
        day_df_list = get_day_result(data)