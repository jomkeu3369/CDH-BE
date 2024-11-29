from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.database import get_db
from api.domain.calendar import calendar_crud, calendar_schema
from api.domain.user import user_router
from api.models import ORM

router = APIRouter(
    prefix="/stack/api/v1",
    tags=["calendar"]
)

# 캘린더 전체 조회 (month)
@router.get("/calendar", response_model=calendar_schema.calendarList)
async def calendar_list(_calendar_get: calendar_schema.calendarGet, db: AsyncSession = Depends(get_db),
                    current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    
    total, _calendar_list = await calendar_crud.search_calendar(db, user=current_user, year=_calendar_get.year, month=_calendar_get.month)
    return {
        'total': total,
        'calendar_list': _calendar_list
    }

# 캘린더 수정
@router.put("/calendar", status_code=status.HTTP_200_OK)
async def calendar_update(_calendar_update: calendar_schema.calendar, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    calendar = await calendar_crud.get_calendar(db, calendar_id=_calendar_update.calendar_id)
    if not calendar:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    if current_user.user_id != calendar.user_info.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    
    await calendar_crud.update_calendar(db=db, db_calendar=calendar, calendar_update=_calendar_update)
    update_calendar = await calendar_crud.get_calendar(db, calendar_id=_calendar_update.calendar_id)
    return update_calendar

# 캘린더 생성
@router.post("/calendar", response_model=calendar_schema.calendar)
async def calendar_create(_calendar_create: calendar_schema.calendarCreate, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    calendar = await calendar_crud.create_calendar(db=db, calendar_create=_calendar_create, user=current_user)
    return calendar
