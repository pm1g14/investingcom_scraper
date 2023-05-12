from selenium.webdriver.common.by import By
from model import RowParameters, CPIEvent
from utils import NumUtils as util
from utils import JsonUtils, DateUtils
from datetime import date
import sys, time, datetime
import logging
logging.basicConfig(filename="applogs", format='%(asctime)s%(message)s', filemode='w')

class Scraper:

    def scrape(url:str, driver):
        pass

class InvestingComScraper(Scraper):

    def scrape(self, driver):
        driver.get(f"https://www.investing.com/economic-calendar/")
        try:
            maybePrivacyPopup = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
        except Exception as e:
            print('Popup accept privacy policy does not exist. Continuing')
        
        time.sleep(6)

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
                
                if (self.__isCPIEvent(event = event) and currency == 'USD'):
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
    

    def __isCPIEvent(self, event:str) -> bool:
        return ("Core CPI (YoY)" in event) or ("CPI (YoY)" in event) or ("Core CPI (MoM)" in event) or ("CPI (MoM)" in event)