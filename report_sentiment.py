from browser_driver import Browser
from selenium.webdriver.common.keys import Keys
from time import sleep
import requests
import os
import plotly.graph_objects as go
import plotly
from av_data import get_data, get_day_result

class ReportBrowser(Browser):
    def __init__(self, download_path):
        super().__init__(self, path=download_path)
        self.tickers = self.get_tickers_SIC()

    def ticker_report(self, ticker):
        # r = requests.get('https://www.sec.gov/edgar/browse/?CIK=' + self.tickers[ticker]) # request fail to get table data (async fetch)
        self.retrieve_html('https://www.sec.gov/edgar/browse/?CIK=' + self.tickers[ticker])
        sleep(1)
        self.browser.find_element_by_id("btnViewAllFilings").click()
        sleep(1)
        self.browser.find_element_by_class_name("buttons-csv").click()
        sleep(1)


    def get_tickers_SIC(self):
        tickers = {}
        with open("ticker_SIC.txt") as f:
            lines = f.readlines()
            for line in lines:
                [ticker, SIC] = line.split()
                tickers[ticker] = SIC
        return tickers

def candle_stick(df):
    # fig = go.Figure(data=[go.Candlestick(
    #     x=df['time'],
    #     open=df['open'],
    #     high=df['high'],
    #     low=df['low'],
    #     close=df['close'])])
    # fig.show()

    plotly.offline.plot({
        "data": [go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'])]
    }, auto_open=True)

def rename_file(rel_path, ticker):
    abs_path = os.path.abspath(rel_path)
    os.rename(abs_path + "\\EDGAR Entity Landing Page.csv", abs_path + ("\\%s.csv") % (ticker) )

if __name__ == "__main__":
    browser = ReportBrowser(download_path="./csv")
    tickers = ['aapl', 'msft', 'amzn']
    for ticker in tickers:
        # browser.ticker_report(ticker)
        # rename_file("./csv", ticker)
        data = get_data(ticker, get_all=True)
        day_df_list = get_day_result(data)
        for df in day_df_list:
            candle_stick(df)
