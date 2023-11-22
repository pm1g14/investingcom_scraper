import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from model import RowParameters
from utils import NumUtils as util
from utils import JsonUtils, DateUtils
from publisher import ZmqPublisher
from scraper import InvestingComLightWeightScraper, InvestingComCsScaper, InvestingComScraper
from bs4 import BeautifulSoup as BSoup
from selenium.webdriver.support.ui import WebDriverWait
from optional import Optional
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

import logging, time
import cfscrape

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
    service = Service(executable_path="/usr/bin/chromedriver/chromedriver")
    driver = webdriver.Chrome(options = chrome_options, service=service)
    return driver
    

def invoke_scraper():
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

def invoke_cs_scraper():
    publisher =  ZmqPublisher()

    while True:
        start_timestamp = time.time()

        scraper = cfscrape.create_scraper()
        response = scraper.get(f"https://www.investing.com/economic-calendar/")
        investing_com_cs_scraper = InvestingComCsScaper()
        rows = investing_com_cs_scraper.scrape(driver = response)
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

def getParam(parameter:str, args) -> str | None:
    if args[0] == parameter:
        value = args[1]
    elif args[2] == parameter:
        value = args[3]
    else:
        value = None
    return value

def process_input():
    try:
        args = sys.argv[1:]
        maybe_event_to_wait_for = getParam("--liveEventToWaitFor", args)
        maybe_currency = getParam("--currency", args)
        return maybe_event_to_wait_for, maybe_currency
    except Exception:
        return None, None

def invoke_selenium_scraper():
    publisher =  ZmqPublisher()
    scraper = InvestingComScraper()
    driver = getDriver()
    maybe_live_event_to_wait_for, currency = process_input()

    def parse_page_for_event():
        logging.debug(f'Starting parsing at: {time.time()}')
        start_timestamp = time.time()

        driver.get(f"https://www.investing.com/economic-calendar/")
        rows = scraper.scrape(driver, maybe_live_event_to_wait_for, currency)
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

    if maybe_live_event_to_wait_for or currency:
        parse_page_for_event()
    else:
        while True:
            parse_page_for_event()


if __name__ == '__main__':
    invoke_selenium_scraper()
    