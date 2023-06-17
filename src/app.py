from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from model import RowParameters
from utils import NumUtils as util
from utils import JsonUtils, DateUtils
from publisher import ZmqPublisher
from scraper import InvestingComLightWeightScraper
from bs4 import BeautifulSoup as BSoup

import logging, time

logging.basicConfig(filename="applogs", format='%(asctime)s%(message)s', filemode='w')


    
def filterRows(rows: RowParameters, event:str, curr:str):
    filtered = []
    for row in rows:
        if (event in row.event):
            filtered.append(row)
    return filtered


def getDriver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-cache")
    driver = webdriver.Chrome(options = chrome_options)
    return driver


if __name__ == '__main__':
    publisher =  ZmqPublisher()
    investingcom_scraper = InvestingComLightWeightScraper()

    while True:
        driver = getDriver()
        start_timestamp = time.time()
        logging.debug(f'Starting parsing at: {time.time()}')
        driver.get(f"https://www.investing.com/economic-calendar/")
        rows = investingcom_scraper.scrape(driver)
        #send with zeromq
        message:dict = JsonUtils().convertListToJson(elements= rows)
        logging.info(message)
        print(message)

        if rows:
            publisher.publish(message=message)

        end_timestamp = time.time()
        final = end_timestamp - start_timestamp
        print(f'Time to load and scrape: {final} seconds')
        logging.debug(f'Time to load and scrape: {final} seconds')
        driver.close()
