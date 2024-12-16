from datetime import datetime
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api.models.ORM import Notes, UserInfo, Group
from api.domain.note import note_schema, note_crud
from api.domain.teamspace import teamspace_crud

async def search_notes(db: AsyncSession, user: UserInfo, skip: int = 0, limit: int = 10, keyword: str = ''):
    group_query = select(Group.id).filter(
        func.json_contains(Group.members, f'{{"user_id": {user.user_id}}}').is_(True)
    )
    group_ids = (await db.execute(group_query)).scalars().all()
    query = select(Notes).filter(
        (Notes.user_id == user.user_id) | (Notes.teamspace_id.in_(group_ids))
    )

    if keyword:
        query = query.where(
            Notes.title.contains(keyword) | Notes.content.contains(keyword)
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    note_list = await db.execute(
        query.order_by(Notes.created_at.desc())
             .offset(skip)
             .limit(limit)
    )

    return total, note_list.scalars().all()

async def get_note(db: AsyncSession, note_id: int) -> Notes:
    qeustion = await db.scalars(
        select(Notes)
        .options(
            selectinload(Notes.api),
            selectinload(Notes.erd)
        )
        .where(Notes.note_id == note_id)
    )
    return qeustion.first()

async def get_note_with_teamspaceID(db: AsyncSession, teamspace_id: int) -> Notes:
    qeustion = await db.scalars(
        select(Notes)
        .where(Notes.teamspace_id == teamspace_id)
    )
    return qeustion.first()

async def create_note(db: AsyncSession, note_create: note_schema.NoteCreate, user: UserInfo):
    db_note = Notes(title=note_create.title,
                           content=note_create.content,
                           user_id=user.user_id)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note

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

async def is_use(db: AsyncSession, note_id:int, user_id:int):

    note = await note_crud.get_note(db, note_id=note_id)
    if not note:
        return False
    
    group = None
    if note.teamspace_id is not None:
        group = await teamspace_crud.get_teamspace(db=db, teamspcae_id=note.teamspace_id)

    if group is None: # 팀스페이스가 아닐 때
        if note.user_id != user_id: # 본인 노트가 아니면 오류
            return False
        
    else: # 팀스페이스가 있다면
        if not any(member["user_id"] == user_id for member in group.members): # 팀스페이스 목록에 본인이 없다면 오류
            return False
        
    return True