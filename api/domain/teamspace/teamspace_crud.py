from passlib.context import CryptContext
import uuid
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from api.domain.teamspace import teamspace_schema
from api.models.ORM import UserInfo, Group, Notes
from datetime import datetime

async def get_teamspace(db: AsyncSession, teamspcae_id: int) -> Group:
    qeustion = await db.scalars(
        select(Group)
        .where(Group.id == teamspcae_id)
    )
    return qeustion.first()

async def create_teamspace(db: AsyncSession, teamspace_create:teamspace_schema.TeamspaceChange, note: Notes, user: UserInfo):
    
    db_teamspace = Group(
        user_id=user.user_id,
        members=[{"user_id":user.user_id,"nickname":user.nickname,"email":user.email,"joinedat":(datetime.now()).strftime("%Y-%m-%d %H:%M:%S")}],
        invite_id=str(uuid.uuid4())
    )
    db.add(db_teamspace)
    await db.commit()
    await db.refresh(db_teamspace)

    note.teamspace_id = db_teamspace.id
    db.add(note)
    await db.commit()
    await db.refresh(note)

    return db_teamspace

