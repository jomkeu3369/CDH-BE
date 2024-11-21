from datetime import datetime
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api.models.ORM import Notes, UserInfo, API
from api.domain.api import api_schema

async def get_api(db: AsyncSession, note_id: int, api_id: int):
    qeustion = await db.execute(select(API).filter(
        (API.note_id == note_id) | 
        (API.api_id == api_id)
        )
    )
    return qeustion.scalar_one_or_none()

async def create_api(db: AsyncSession, api_create: api_schema.APICreate):
    db_api = API(note_id=api_create.note_id)
    db.add(db_api)
    await db.commit()
    await db.refresh(db_api)

async def update_api(db: AsyncSession, db_api: API, api_update: api_schema.APIUpdate):
    db_api.title = api_update.title
    db_api.content = api_update.content
    db_api.update_at = datetime.now()
    db.add(db_api)
    await db.commit()
    await db.refresh(db_api)

async def delete_api(db: AsyncSession, db_api: API):
    await db.delete(db_api)
    await db.commit()