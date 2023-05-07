from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from model import RowParameters
from utils import NumUtils as util
from utils import JsonUtils, DateUtils
import sys, time
from datetime import date
from scraper import InvestingComScraper
import logging

logging.basicConfig(filename="applogs", format='%(asctime)s%(message)s', filemode='w')


    
def filterRows(rows: RowParameters, event:str, curr:str):
    filtered = []
    for row in rows:
        if (event in row.event):
            filtered.append(row)
    return filtered


def getDriver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options = chrome_options)
    return driver


if __name__ == '__main__':
    investingcom_scraper = InvestingComScraper()

    while True:
        driver = getDriver()
        rows = investingcom_scraper.scrape(driver)
        #send with zeromq
        message:dict = JsonUtils().convertListToJson(elements= rows)
        logging.info(message)
        print(message)

        time.sleep(3)
