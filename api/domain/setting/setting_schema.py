
from pydantic import BaseModel, field_validator

class settingCreate(BaseModel):
    theme: str
    font_size: int

    @field_validator('theme', mode='before')
    def theme_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('theme는 빈 값이 허용되지 않습니다.')
        return v

    @field_validator('font_size', mode='before')
    def font_size_valid(cls, v):
        if v <= 0:
            raise ValueError('font size는 0보다 커야 합니다.')
        return v

class settingResponse(BaseModel):
    user_id: int
    theme: str
    font_size: int