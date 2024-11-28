from pydantic import BaseModel
import datetime

class calendar(BaseModel):
    calendar_id: int
    content: str
    time: datetime.datetime
    
class calendarGet(BaseModel):
    year: int
    month: int

class calendarCreate(BaseModel):
    content: str
    time: datetime.datetime

class calendarList(BaseModel):
    total: int = 0
    calendar_list: list[calendar] = []