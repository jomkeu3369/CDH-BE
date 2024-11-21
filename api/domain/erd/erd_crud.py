from datetime import datetime
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api.models.ORM import Notes, UserInfo, ERD
from api.domain.erd import erd_schema

async def get_erd(db: AsyncSession, note_id: int, erd_id: int):
    qeustion = await db.execute(select(ERD).filter(
        (ERD.note_id == note_id) | 
        (ERD.note_id == erd_id)
        )
    )
    return qeustion.scalar_one_or_none()

async def create_erd(db: AsyncSession, erd_create: erd_schema.ERDCreate):
    db_erd = ERD(note_id=erd_create.note_id)
    db.add(db_erd)
    await db.commit()
    await db.refresh(db_erd)

async def update_erd(db: AsyncSession, db_erd: ERD, erd_update: erd_schema.ERDUpdate):
    db_erd.title = erd_update.title
    db_erd.content = erd_update.content
    db_erd.updated_at = datetime.now()
    db.add(db_erd)
    await db.commit()
    await db.refresh(db_erd)

async def delete_erd(db: AsyncSession, db_erd: ERD):
    await db.delete(db_erd)
    await db.commit()