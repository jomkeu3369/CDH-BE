from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import datetime


class ERDs(BaseModel):
    erd_id: int
    note_id: int
    title: str | None = None
    content: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None

    class Config:
        orm_mode = True
        
class ERDCreate(BaseModel):
    note_id: int
    user_id: int

class ERDUpdate(BaseModel):
    title: str
    content: str