from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import os

windows_driver_path = "./web_driver/geckodriver.exe"
mac_driver_path = "./web_driver/geckodriver"
log_path = "./web_driver/geckodriver.log"
class Browser():

    def __init__(self, sleeptime = 10, headless=False, path=None):
        self.sleeptime = sleeptime
        self.headless = headless
        self.browser = None
        if path:
            # see https://stackoverflow.com/questions/45097302/download-and-save-multiple-csv-files-using-selenium-and-python-from-popup
            abs_path = os.path.abspath(path)
            self.profile = webdriver.FirefoxProfile()
            self.profile.set_preference("browser.download.dir", abs_path)
            self.profile.set_preference("browser.download.folderList", 2)
            self.profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
        else:
            self.profile = None

    def get_browser(self):
        if not self.browser:
            options = Options()
            options.headless = self.headless
            if self.profile:
                self.browser = webdriver.Firefox(firefox_profile=self.profile, executable_path=windows_driver_path, log_path=log_path, options=options)
            else:
                self.browser = webdriver.Firefox(executable_path=windows_driver_path,
                                                 log_path=log_path, options=options)
        return self.browser

    def get_body_innerHTML(self):
        trial, exception = 0, None
        while trial < 60:
            sleep(1)
            try:
                return self.browser.execute_script("return document.body.innerHTML")
            except Exception as ex:
                trial += 1
                print('trial:', trial)
                exception = ex
        raise exception

    def retrieve_html(self, url):
        self.get_browser().get(url)
        return self.get_body_innerHTML()

    def click_thru(self, link_text):
        sleep(5)
        self.get_browser().find_element_by_link_text(link_text).click()
        return self.get_body_innerHTML()

    def click_thru_by_class(self, classname):
        sleep(5)
        self.get_browser().find_element_by_class_name(classname).click()
        return self.get_body_innerHTML()

    def close_session(self):
        if self.browser:
            self.browser.quit()

    def wait_and_retrieve(self, url, classname=''):
        self.get_browser().get(url)
        try:
            element = WebDriverWait(self.get_browser(), 120).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, classname)))
            return element.text
        except Exception as e:
            print(e)
            return None

    def wait_and_retrieve_by_xpath(self,url, xpath=''):
        try:
            element = WebDriverWait(self.get_browser(), 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            return element
        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    browser = Browser()
    print(browser.retrieve_html('https://www.sec.gov/edgar/searchedgar/companysearch.html'))  #input('>')))
    browser.browser.find_element_by_id("company").send_keys("APPL")



