from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import datetime

class APIs(BaseModel):
    api_id: int
    note_id: int
    title: str | None = None
    content: str | None = None
    updated_at: datetime.datetime | None = None

    class Config:
        orm_mode = True
        
class APICreate(BaseModel):
    note_id: int
    user_id: int

class APIUpdate(BaseModel):
    title: list[str]
    content: list[str] 