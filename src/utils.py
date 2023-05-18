from optional import Optional
from model import Event
from model import RowParameters
from model import MyEncoder
from typing import List
from datetime import date
import calendar
import time
import json

class NumUtils:

    def stringToFloat(value) -> Optional:
        try:
            return Optional.of(float(value.replace(',', '')))
        except ValueError:
            return Optional.empty
        

class JsonUtils:

    def convertListToJson(self, elements:List[RowParameters]):
        current_GMT = time.gmtime()
        time_stamp = calendar.timegm(current_GMT)
        array = []
        for element in elements:
            array.append(element.__dict__)
        return json.dumps(Event(rows=array, timestamp=time_stamp).__dict__, cls=MyEncoder, indent=4)


class DateUtils:

    def getInvestingComDateFormat(date:date) -> str:
        format = r"%b %d %Y"
        try:
            desiredFormat = date.strftime(format)
            return desiredFormat
        except Exception as e:
            print('Cannot convert given date to the desired format.')
            return ''

    def getDateInCorrectFormat(date:date) -> str:
        format = r"%b%d.%Y"
        try:
            desiredFormat = date.strftime(format)
            return desiredFormat.lower()
        except Exception as e:
            print('Cannot convert given date to the desired format.')
            return ''