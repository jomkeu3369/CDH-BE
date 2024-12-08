from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import datetime

class NoteRequest(BaseModel):
    pass

class NoteCreateSuccess(BaseModel):
    user_id: int
    note_id: int
    api_id: int
    erd_id: int
    
class Notes(BaseModel):
    note_id: int
    user_id: int
    title: str
    content: str
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None

    class Config:
        orm_mode = True

class NoteResponse(BaseModel):
    note_id: int
    user_id: int
    title: str
    content: str
    is_teamspace: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None

class NoteCreate(BaseModel):
    title: str
    content: str

    @field_validator('title', 'content', mode='before')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v
    
class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteListResponse(BaseModel):
    note_id: int
    user_id: int
    content: str
    title: str
    teamspace_id: int | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None
    erd_id: Optional[int] = None
    api_id: Optional[int] = None

class NoteList(BaseModel):
    total: int = 0
    note_list: list[NoteListResponse] = []
