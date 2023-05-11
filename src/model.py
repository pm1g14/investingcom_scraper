from enum import Enum
from optional import Optional, something
from attr import dataclass
from typing import List
import json

@dataclass(frozen=True)
class RowParameters:

    date: str
    time: str
    currency: str
    event: str
    actual: Optional
    forecast: Optional
    previous: Optional

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, something.Something):
            return str(obj.get())
        else:
            return ""
           


@dataclass(frozen=True)
class Event:
    rows: List[RowParameters]
    timestamp: str
    

class CPIEvent(str, Enum):
    CPI_M_M = 'CPI m/m'
    CORE_CPI_M_M = 'Core CPI m/m'
    CPI_Y_Y = 'CPI y/y'
    CORE_CPI_Y_Y = 'Core CPI y/y'
    DEFAULT = ''

    def toCPIEvent(event:str):
        if (event == 'Core CPI (YoY)'):
            return CPIEvent.CORE_CPI_Y_Y

        elif (event == 'CPI (YoY)'):
            return CPIEvent.CPI_Y_Y
        
        elif (event == 'Core CPI (MoM)'):
            return CPIEvent.CORE_CPI_M_M
        
        elif (event == 'CPI (MoM)'):
            return CPIEvent.CPI_M_M
        
        else:
            return CPIEvent.DEFAULT