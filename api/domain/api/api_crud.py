from datetime import datetime
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api.models.ORM import Notes, UserInfo, API
from api.domain.api import api_schema

async def get_api_by_note_id(db: AsyncSession, note_id: int):
    query =  await db.execute(
        select(API).where(API.note_id == note_id)
    )
    return query.scalars().first()

async def get_api(db: AsyncSession, note_id: int, api_id: int) -> API:
    query = await db.execute(
        select(API)
        .options(selectinload(API.notes))
        .filter(
            (API.note_id == note_id) & 
            (API.api_id == api_id)
        )
    )
    return query.scalar_one_or_none()

async def create_api(db: AsyncSession, api_create: api_schema.APICreate):
    db_api = API(note_id=api_create.note_id, user_id=api_create.user_id)
    db.add(db_api)
    await db.commit()
    await db.refresh(db_api)
    return db_api

async def update_api(db: AsyncSession, db_api: API, api_update: api_schema.APIUpdate):
    db_api.title = api_update.title
    db_api.content = api_update.content
    db_api.updated_at = datetime.now()
    db.add(db_api)
    await db.commit()
    await db.refresh(db_api)

async def delete_api(db: AsyncSession, db_api: API):
    await db.delete(db_api)
    await db.commit()