from datetime import datetime
from sqlalchemy import select, func
import os

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api.models.ORM import Notes, UserInfo, ERD
from api.domain.erd import erd_schema

UPLOAD_DIR = "erd_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def get_erd_by_note_id(db: AsyncSession, note_id: int):
    query = await db.execute(
        select(ERD).where(ERD.note_id == note_id)
    )
    
    return query.scalars().first()

async def get_erd(db: AsyncSession, note_id: int, erd_id: int) -> ERD:
    query = await db.execute(
        select(ERD)
        .options(selectinload(ERD.notes))
        .filter(
            (ERD.note_id == note_id) &
            (ERD.erd_id == erd_id)
        )
    )
    return query.scalar_one_or_none()

async def create_erd(db: AsyncSession, erd_create: erd_schema.ERDCreate):
    db_erd = ERD(note_id=erd_create.note_id, user_id=erd_create.user_id)
    db.add(db_erd)
    await db.commit()
    await db.refresh(db_erd)
    return db_erd

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

async def upload_erd(file, note_id:int, erd_id:int):
    file_path = os.path.join(UPLOAD_DIR, f"note_{note_id}_erd_{erd_id}.png")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

async def get_uploaded_erd(note_id:int, erd_id:int):
    file_path = os.path.join(UPLOAD_DIR, f"note_{note_id}_erd_{erd_id}.png")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")

    return file_path

