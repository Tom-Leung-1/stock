import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
key = open('./config/key.txt').read()
from datetime import date, datetime, timedelta, time


def get_data(ticker, get_all=False, interval="1min", slice="year1month1"):
    df = None
    if get_all:
        ts = TimeSeries(key=key, output_format='csv')
        data = ts.get_intraday_extended(symbol=ticker, interval=interval, slice=slice) # change slice
        data_list = list(data[0])
        df = pd.DataFrame(data_list[1:], columns=data_list[0])
        header_list = ['open', 'high', 'low', 'close', 'volume']
        for h in header_list:
            df[h] = df[h].astype(float)
        df['time'] = df.apply(lambda row: datetime.strptime(row.time, "%Y-%m-%d %H:%M:%S"), axis=1)
    else: # latest 1-2 month data
        ts = TimeSeries(key=key, output_format='pandas')
        data = ts.get_intraday(symbol=ticker, interval=interval, outputsize="full")
        df = pd.DataFrame(data[0])
        df["time"] = df.index
        df = df.rename(columns={x:x.split()[-1] for x in df.columns})
    df = df[::-1]
    df['date'] = df.apply(lambda row: row.time.date(), axis=1)
    df['datetime'] = df.apply(lambda row: row.time.time(), axis=1)
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

def get_month_df(df): #to be verified
    df['time'] = pd.to_datetime(df['time'])
    df['date_month'] = df.apply(lambda row: row.time.month, axis=1)
    df['date_year'] = df.apply(lambda row: row.time.year, axis=1)
    start_month = df.iloc[0]['date_month']
    start_year = df.iloc[0]['date_year']
    end_month = df.iloc[-1]['date_month']
    end_year = df.iloc[-1]['date_year']
    month_df_list = []
    while start_month <= end_month and start_year <= end_year:
        month_df = df.loc[(df['date_month'] == start_month) & (df['date_year'] == start_year)]
        start_year = start_year + 1 if start_month == 12 else start_year
        start_month = 1 if start_month == 12 else start_month + 1
        month_df_list.append(month_df)
    return month_df_list

def get_months_data(months, ticker):
    for m in range(months):
        slice = "year1month" + str(m+1)
        df = get_data(ticker, get_all=True, interval="1min", slice=slice)
        start_month = df.iloc[0]['date'].month
        start_year = df.iloc[0]['date'].year
        name = '%s-%s-%s' % (start_month, start_year, ticker)
        df.to_csv("./csv/" + name + ".csv", index=False)

def combine_months_data(start, end, ticker):
    df_list = []
    start_month, start_year = start.split("-")
    end_month, end_year = end.split("-")
    start_month, start_year, end_month, end_year = [int(start_month), int(start_year), int(end_month), int(end_year)]
    while start_month <= end_month and start_year <= end_year:
        df = pd.read_csv("./csv/%d-%d-%s" % (start_month, start_year, ticker) + ".csv")
        df_list.append(df)
        start_year = start_year + 1 if start_month == 12 else start_year
        start_month = 1 if start_month == 12 else start_month + 1
    month_df = pd.concat(df_list)
    return month_df

if __name__ == '__main__':
    # ticker = input("ticker name: ") # ETF: DIA, SPY, QQQ
    tickers = ["AAPL"]
    for ticker in tickers:
        print("---------------------------------" "\n" + ticker)
        # data = get_data(ticker, get_all=True)
        # day_df_list = get_day_result(data)
        # get_months_data(3, ticker)
        combine_months_data("6-2021", "8-2021", ticker)