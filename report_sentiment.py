from browser_driver import Browser
from selenium.webdriver.common.keys import Keys
from time import sleep
import requests

class ReportBrowser(Browser):
    def __init__(self):
        super().__init__(self)
        self.tickers = self.get_tickers_SIC()

    def ticker_report(self, ticker):
        # r = requests.get('https://www.sec.gov/edgar/browse/?CIK=' + self.tickers[ticker]) # request fail to get table data (async fetch)
        self.retrieve_html('https://www.sec.gov/edgar/browse/?CIK=' + self.tickers[ticker])
        reports = self.browser.find_elements_by_xpath("//tbody/tr")
        reports
        # self.browser.find_element_by_id("btnViewAllFilings").click()
        # self.browser.find_element_by_id("company").send_keys(Keys.ENTER)
        # smart-search-entity-hints table

    def get_tickers_SIC(self):
        tickers = {}
        with open("ticker_SIC.txt") as f:
            lines = f.readlines()
            for line in lines:
                [ticker, SIC] = line.split()
                tickers[ticker] = SIC
        return tickers

if __name__ == "__main__":
    browser = ReportBrowser()
    browser.ticker_report('aapl')
    browser