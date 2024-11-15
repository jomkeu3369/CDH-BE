from datetime import datetime
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api.models.ORM import Notes, UserInfo
from api.domain.note import note_schema

async def search_notes(db: AsyncSession, user: UserInfo, skip: int = 0, limit: int = 10, keyword: str = ''):
    query = select(Notes).filter(Notes.user_id == user.user_id)
    
    if keyword:
        query = query.where(Notes.title.contains(keyword) | Notes.content.contains(keyword))
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    
    note_list = await db.execute(query.offset(skip).limit(limit)
                                     .order_by(Notes.created_at.desc())
                                     .distinct())
    
    return total, note_list.scalars().all()

async def get_note(db: AsyncSession, note_id: int):
    qeustion = await db.execute(select(Notes).filter(Notes.note_id == note_id))
    return qeustion.scalar_one_or_none()

async def create_note(db: AsyncSession, note_create: note_schema.NoteCreate, user: UserInfo):
    db_note = Notes(title=note_create.title,
                           content=note_create.content,
                           user_id=user.user_id)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)

async def update_note(db: AsyncSession, db_note: Notes, note_update: note_schema.NoteUpdate):
    if note_update.title is not None:
        db_note.title = note_update.title
    if note_update.content is not None:   
        db_note.content = note_update.content
    db_note.updated_at = datetime.now()
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)

async def delete_note(db: AsyncSession, db_note: Notes):
    await db.delete(db_note)
    await db.commit()