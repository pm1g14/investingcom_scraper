from selenium.webdriver.common.by import By
from model import RowParameters, CPIEvent
from utils import NumUtils as util
from utils import JsonUtils, DateUtils
from datetime import date
from bs4 import BeautifulSoup as BSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import sys, datetime
import logging, time 
import requests
logging.basicConfig(filename="applogs", format='%(asctime)s%(message)s', filemode='w')

class Scraper:

    def scrape(url:str, driver):
        pass
    
    def _isCPIEvent(self, event:str) -> bool:
        return ("Core CPI (YoY)" in event) or ("CPI (YoY)" in event) or ("Core CPI (MoM)" in event) or ("CPI (MoM)" in event)

class InvestingComLightWeightScraper(Scraper):

    def scrape(self: str, driver):
        dom = driver.page_source
        bs_obj = BSoup(dom, 'html.parser')
        rows = bs_obj.find_all(id="economicCalendarData")[0].find_all('tbody')[0].find_all('tr')
        result = []
        count = 0
        for row in rows:
            try:
                cells = row.find_all('td')

                if (count == 0):
                    date = cells[0].get_text()
                    count += 1
                    continue
            
                eventTime = cells[0].get_text()
                currency = cells[1].get_text()
                event = cells[3].get_text()
                actual = cells[4].get_text()
                forecast = cells[5].get_text()
                previous = cells[6].get_text()

                if ("%" in actual):
                    actual = actual.replace('%', '')
                if "%" in forecast:
                    forecast = forecast.replace('%', '')
                if "%" in previous:
                    previous = previous.replace('%', '')

                if ("B" in actual):
                    actual = actual.replace('B', '')
                if "B" in forecast:
                    forecast = forecast.replace('B', '')
                if "B" in previous:
                    previous = previous.replace('B', '')

                if ("K" in actual):
                    actual = actual.replace('K', '')
                if "K" in forecast:
                    forecast = forecast.replace('K', '')
                if "K" in previous:
                    previous = previous.replace('K', '')
                
                if (super()._isCPIEvent(event = event) and currency == 'USD'):
                    event:str = CPIEvent.toCPIEvent(event).value
                    logging.info(f"Time actual got updated is: {datetime.datetime.now().strftime('%H:%M:%S')}")
                    print(f"Time actual got updated is: {datetime.datetime.now().strftime('%H:%M:%S')}") 

                rowParams = RowParameters(
                    date = date, 
                    time = eventTime, 
                    currency = currency.strip(), 
                    event = event.strip(), 
                    actual = util.stringToFloat(actual.strip()), 
                    forecast = util.stringToFloat(forecast.strip()),
                    previous = util.stringToFloat(previous.strip())
                )
                result.append(rowParams)
                count += 1
            except Exception as e:
                print(e)
                continue
        return result
    



class InvestingComScraper(Scraper):

    def scrape(self, driver):
       
        try:    
            maybePrivacyPopup = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
        except Exception as e:
            print('Popup accept privacy policy does not exist. Continuing')
        
        time.sleep(4)

        try:
        
           maybeSignupPopup = driver.find_element(By.XPATH, '//*[@id="PromoteSignUpPopUp"]/div[2]/i').click()
        except Exception as e2:
            print('Popup signup does not exist. Continuing..')

        table = driver.find_element(By.XPATH, '//*[@id="economicCalendarData"]')
        rows = []
        index = 1
        for row in table.find_elements(By.TAG_NAME, 'tr'):
            index += 1
            try:
                nowDate = date.today()
                nowDateFormatted = DateUtils.getInvestingComDateFormat(date = nowDate)
                event = driver.find_element(By.XPATH, f'/html/body/div[5]/section/div[6]/table/tbody/tr[{index}]/td[4]').text
                eventTime = row.find_element(By.XPATH, f'/html/body/div[5]/section/div[6]/table/tbody/tr[{index}]/td[1]').text
                currency = row.find_element(By.XPATH, f'/html/body/div[5]/section/div[6]/table/tbody/tr[{index}]/td[2]').text
                actual = row.find_element(By.XPATH, f'/html/body/div[5]/section/div[6]/table/tbody/tr[{index}]/td[5]').text
                forecast = row.find_element(By.XPATH, f'/html/body/div[5]/section/div[6]/table/tbody/tr[{index}]/td[6]').text
                previous = row.find_element(By.XPATH, f'/html/body/div[5]/section/div[6]/table/tbody/tr[{index}]/td[7]').text
                
                if ("%" in actual):
                    actual = actual.replace('%', '')
                if "%" in forecast:
                    forecast = forecast.replace('%', '')
                if "%" in previous:
                    previous = previous.replace('%', '')

                if ("B" in actual):
                    actual = actual.replace('B', '')
                if "B" in forecast:
                    forecast = forecast.replace('B', '')
                if "B" in previous:
                    previous = previous.replace('B', '')

                if ("K" in actual):
                    actual = actual.replace('K', '')
                if "K" in forecast:
                    forecast = forecast.replace('K', '')
                if "K" in previous:
                    previous = previous.replace('K', '')
                
                if (super()._isCPIEvent(event = event) and currency == 'USD'):
                    event:str = CPIEvent.toCPIEvent(event).value
                    logging.info(f"Time actual got updated is: {datetime.datetime.now().strftime('%H:%M:%S')}")
                    print(f"Time actual got updated is: {datetime.datetime.now().strftime('%H:%M:%S')}") 
                    

                rowParams = RowParameters(
                    date = nowDateFormatted, 
                    time = eventTime, 
                    currency = currency.strip(), 
                    event = event.strip(), 
                    actual = util.stringToFloat(actual.strip()), 
                    forecast = util.stringToFloat(forecast.strip()),
                    previous = util.stringToFloat(previous.strip())
                )
                rows.append(rowParams)
            except Exception as e:
                print(e)
                continue
        return rows
    