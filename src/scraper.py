from selenium.webdriver.common.by import By
from model import RowParameters, CPIEvent
from utils import NumUtils as util
from utils import JsonUtils, DateUtils
from datetime import date, timedelta
from bs4 import BeautifulSoup as BSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import sys, datetime
import logging, time, pytz
import requests
logging.basicConfig(filename="applogs", format='%(asctime)s%(message)s', filemode='w')

class Scraper:

    def scrape(url:str, driver, maybeEventToWaitFor: str | None = None, maybeCurrency: str | None = None):
        pass
    
    def _isCPIEvent(self, event:str) -> bool:
        return ("Core CPI (YoY)" in event) or ("CPI (YoY)" in event) or ("Core CPI (MoM)" in event) or ("CPI (MoM)" in event)


class InvestingComCsScaper(Scraper):

    def scrape(self, driver, maybeEventToWaitFor = None, maybeCurrency = None):
        soup = BSoup(driver.text, 'html.parser')
        rows = soup.find_all(id="economicCalendarData")[0].find_all('tbody')[0].find_all('tr')
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

class InvestingComLightWeightScraper(Scraper):

    def scrape(self: str, driver, maybeEventToWaitFor: str | None = None, maybeCurrency: str | None = None):
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
                
                if (super()._isCPIEvent(event = event) and 'USD' in currency):
                    event:str = CPIEvent.toCPIEvent(event).value

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

    def text_to_be_present_in_element(self, locator, text_):

        def _predicate(driver):
            try:
                element_text = driver.find_element(*locator).text
                return  element_text.strip() != ''
            except Exception:
                return False

        return _predicate

    @staticmethod
    def __isPastEvent(eventTime: str) -> bool:
        gmt_minus_4 = pytz.timezone('Etc/GMT+4')

        if 'min' in eventTime:
            eventTimeStr = eventTime.replace('min', '')
            try:
                toMin = int(eventTimeStr.strip())
                nowDatetime = datetime.datetime.utcnow()
                current_gmt_minus_4 = nowDatetime.replace(tzinfo=pytz.UTC).astimezone(gmt_minus_4)
                eventDatetime = current_gmt_minus_4 + timedelta(minutes=toMin)
                return current_gmt_minus_4.timestamp() - eventDatetime.timestamp() >= 120
            except Exception:
                print("Cannot convert minutes string to a number")
                return True
        else:
            eventTimeStr = f'{eventTime}:00'
            eventDatetime = DateUtils.convertDateAndTimeStrToDatetime(eventTimeStr, date.today()).timestamp()
            if eventDatetime:
                nowDatetime = datetime.datetime.utcnow()
                current_gmt_minus_4 = nowDatetime.replace(tzinfo=pytz.UTC).astimezone(gmt_minus_4)
                return current_gmt_minus_4.timestamp() - eventDatetime >= 120
            return True

    def scrape(self, driver, maybeEventToWaitFor: str | None, maybeCurrency: str | None):
       
        # try:    
        #     maybePrivacyPopup = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
        # except Exception as e:
        #     print('Popup accept privacy policy does not exist. Continuing')
        
        # time.sleep(4)

        # try:
        
        #    maybeSignupPopup = driver.find_element(By.XPATH, '//*[@id="PromoteSignUpPopUp"]/div[2]/i').click()
        # except Exception as e2:
        #     print('Popup signup does not exist. Continuing..')
        table = driver.find_element(By.XPATH, '//*[@id="economicCalendarData"]')
        rows = []
        index = 1
        for row in table.find_elements(By.TAG_NAME, 'tr'):
            index += 1
            mostRecentEvent = False
            try:
                nowDate = date.today()
                nowDateFormatted = DateUtils.getInvestingComDateFormat(date = nowDate)
                event = driver.find_element(By.XPATH, f'/html/body/div[6]/section/div[6]/table/tbody/tr[{index}]/td[4]').text
                eventTime = row.find_element(By.XPATH, f'/html/body/div[6]/section/div[6]/table/tbody/tr[{index}]/td[1]').text
                currency = row.find_element(By.XPATH, f'/html/body/div[6]/section/div[6]/table/tbody/tr[{index}]/td[2]').text
                forecast = row.find_element(By.XPATH, f'/html/body/div[6]/section/div[6]/table/tbody/tr[{index}]/td[6]').text
                previous = row.find_element(By.XPATH, f'/html/body/div[6]/section/div[6]/table/tbody/tr[{index}]/td[7]').text
                
                isPastEvent = InvestingComScraper.__isPastEvent(eventTime)
                
                if not isPastEvent and (maybeCurrency and maybeEventToWaitFor):
                    if event == maybeEventToWaitFor and currency == currency:
                    
                        try:
                            actual = row.find_element(By.XPATH, f'/html/body/div[6]/section/div[6]/table/tbody/tr[{index}]/td[5]').text
                            WebDriverWait(driver, 6000).until(self.text_to_be_present_in_element(locator=(By.XPATH, f'/html/body/div[6]/section/div[6]/table/tbody/tr[{index}]/td[5]'), text_=''))
                            mostRecentEvent = True
                        except Exception:
                            continue
                    else:
                        continue

                actual = row.find_element(By.XPATH, f'/html/body/div[6]/section/div[6]/table/tbody/tr[{index}]/td[5]').text
                
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
                
                if (super()._isCPIEvent(event = event) and 'USD' in currency):
                    event:str = CPIEvent.toCPIEvent(event).value
                    

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
                if mostRecentEvent:
                    break

            except Exception as e:
                print(e)
                continue
        return rows
