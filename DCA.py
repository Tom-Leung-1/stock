import re
import requests
key = open('./config/key.txt').read() # alpha_vantage_key (change it)
from datetime import datetime
from forex_python.converter import CurrencyRates
import time
from pandas import DataFrame
import pandas as pd

def get_month_data(ticker, key):
    data = None
    while True:
        try:
            # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=%s&apikey=%s' % (ticker, key)
            r = requests.get(url)
            data = r.json()
            return data['Monthly Time Series']
        except Exception as e:
            if 'Note' in data:
                print(data['Note'], "\n wait 1 minute")
                time.sleep(60)
            else:
                print("Unexpected error:", str(e))
                return None

def str_to_date(str):
    return datetime.strptime(str, '%Y-%m-%d')

def get_exchange_rate(date):
    c = CurrencyRates()
    while True:
        try:
            exchange_rate = c.get_rate('USD', 'HKD', date)
            return exchange_rate
        except Exception as e:
            print("Error:", str(e))

def append_date(data_dict, start_year):
    DCA_list = []
    for key in data_dict:
        date = str_to_date(key)
        if date.year < start_year: break
        dict = data_dict[key]
        dict['date'] = date
        DCA_list.append(dict)
    return DCA_list

def DCA_month(instalment, data_dict, year, end_year, ex_rate = False): #assume usd to hkd = 1 : 7.78, but it is not okay
    if (not data_dict): return
    start_year = end_year - year + 1
    DCA_list = append_date(data_dict, start_year)
    withdraw = DCA_list[0]
    DCA_list.reverse()
    total_stock = 0
    remain = 0
    total_investment = 0
    buy_date = DCA_list[0]['date']
    # DCA_df_values = [list(dca.values()) for dca in DCA_list]
    # DCA_df_keys = list(DCA_list[0].keys())
    # df = DataFrame(DCA_df_values, columns=DCA_df_keys)
    for DCA in DCA_list:
        exchange_rate = get_exchange_rate(DCA['date']) if ex_rate else 7.78
        total_investment += instalment
        bought_shares = (instalment / exchange_rate) // float(DCA['1. open'])
        total_stock += bought_shares
        remain += (instalment / exchange_rate) % float(DCA['1. open'])
        if (remain > float(DCA['1. open'])):
            total_stock += remain // float(DCA['1. open'])
            bought_shares += remain // float(DCA['1. open'])
            remain = remain % float(DCA['1. open'])
        print("Date: %d year %d month, bought shares: %d, shares price %f, investment %f, remain %f" % (DCA['date'].year, DCA['date'].month, bought_shares, float(DCA['1. open']), bought_shares * float(DCA['1. open']), remain))
    final_exchange_rate = get_exchange_rate(withdraw['date']) if ex_rate else 7.78
    final_amount = total_stock * float(withdraw['1. open']) * final_exchange_rate + remain
    multiplicity = final_amount / total_investment
    return_rate = (final_amount - total_investment) / total_investment
    annual_return_rate = return_rate / year
    print("final_amount %f, total_investment %f, multiplicity %f, annual_return_rate %f" % (final_amount, total_investment, multiplicity, annual_return_rate))
    return final_amount, total_investment, multiplicity, annual_return_rate, buy_date



def DCA_year(instalment, data_dict, year, end_year, ex_rate = False): #assume usd to hkd = 1 : 7.78, but it is not okay
    if (not data_dict): return
    start_year = end_year - year + 1
    DCA_list = append_date(data_dict, start_year)
    withdraw = DCA_list[0]
    DCA_list.reverse()
    total_stock = 0
    remain = 0
    total_investment = 0
    current_year = -1
    for DCA in DCA_list: #
        total_investment += instalment
        if (current_year != DCA['date'].year):
            exchange_rate = get_exchange_rate(DCA['date']) if ex_rate else 7.78
            current_year = DCA['date'].year
            bought_shares = (instalment / exchange_rate) // float(DCA['1. open'])
            total_stock += bought_shares
            remain += (instalment / exchange_rate) % float(DCA['1. open'])
            if (remain > float(DCA['1. open'])):
                total_stock += remain // float(DCA['1. open'])
                bought_shares += remain // float(DCA['1. open'])
                remain = remain % float(DCA['1. open'])
            print("Date: %d year %d month, bought shares: %d, shares price %f, investment %f, remain %f" % (
            DCA['date'].year, DCA['date'].month, bought_shares, float(DCA['1. open']),
            bought_shares * float(DCA['1. open']), remain))
        else: remain += instalment / exchange_rate
    final_exchange_rate = get_exchange_rate(withdraw['date']) if ex_rate else 7.78
    final_amount = total_stock * float(withdraw['1. open']) * final_exchange_rate + remain
    multiplicity = final_amount / total_investment
    return_rate = (final_amount - total_investment) / total_investment
    annual_return_rate = return_rate / year
    print("final_amount %f, total_investment %f, multiplicity %f annual_return_rate %f" % (final_amount, total_investment, multiplicity, annual_return_rate))
    return final_amount, total_investment, multiplicity, annual_return_rate

def get_sp_tickers(): # please git pull the s-and-p folder to update the latest sp_tickers data
    tickers = []
    with open('./s&p/data/constituents_symbols.txt') as fp:
        Lines = fp.readlines()
        for line in Lines:
            tickers.append(line.strip())
    return tickers

def get_csv():
    df = pd.read_csv("S&P_DCA.csv")
    return df

def string_clean(str):
    return re.sub('\.', "", str)

if __name__ == '__main__':
    tickers = ["VOO", "DIA", "SPY", "QQQ"]
    # tickers = get_sp_tickers()
    df_init = [[t, 0, 0, 0, 0, None] for t in tickers]
    df = DataFrame(df_init, columns=['ticker', 'final_amount', 'total_investment', 'multiplicity', 'annual_return_rate', 'buy_date'])
    # df = get_csv()
    df = df.set_index('ticker')
    df = df.astype(float)
    df['buy_date'] = df['buy_date'].astype('datetime64[ns]')
    for ticker in tickers:
        print("---------------------------------" "\n" + ticker)
        if df.at[ticker, "final_amount"]: continue
        ticker = string_clean(ticker)
        data_dict = get_month_data(ticker, key) # data only 20 years
        print("monthly based")
        final_amount, total_investment, multiplicity, annual_return_rate, buy_date = DCA_month(5000, data_dict, 20, 2021) if data_dict else [0, 0, 0, 0, None]
        df.at[ticker, "final_amount"] = final_amount
        df.at[ticker, "total_investment"] = total_investment
        df.at[ticker, "multiplicity"] = multiplicity
        df.at[ticker, "annual_return_rate"] = annual_return_rate
        df.at[ticker, "buy_date"] = buy_date
        # print("yearly based")
        # final_amount, total_investment, multiplicity, annual_return_rate = DCA_year(5000, data_dict, 20, 2021)
    # df.to_csv("S&P_DCA.csv")
    df = df.sort_values(by=['annual_return_rate'], ascending=False)
    df.to_csv("ETF_DCA.csv")