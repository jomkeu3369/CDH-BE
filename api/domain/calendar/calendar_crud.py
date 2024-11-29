from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy import extract

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api.models.ORM import Calendars, UserInfo
from api.domain.calendar import calendar_schema

async def search_calendar(db: AsyncSession, user: UserInfo, year: int, month: int):
    result = await db.execute(
        select(Calendars).filter(
            Calendars.user_id == user.user_id,
            extract('year', Calendars.time) == year,
            extract('month', Calendars.time) == month
        )
    )
    calendar_list = result.scalars().all()
    return len(calendar_list), calendar_list

async def get_calendar(db: AsyncSession, calendar_id: int):
    qeustion = await db.scalars(
        select(Calendars)
        .where(Calendars.calendar_id == calendar_id)
    )
    return qeustion.one_or_none()

async def update_calendar(db: AsyncSession, db_calendar: Calendars, calendar_update: calendar_schema.calendar):
    db_calendar.content = calendar_update.content
    db.add(db_calendar)
    await db.commit()
    await db.refresh(db_calendar)

async def create_calendar(db: AsyncSession, calendar_create: calendar_schema.calendarCreate, user: UserInfo):
    db_calendar = Calendars(content=calendar_create.content,
                        user_id=user.user_id,
                        time=calendar_create.time)
    db.add(db_calendar)
    await db.commit()
    await db.refresh(db_calendar)
    return db_calendar

