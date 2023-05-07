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
    