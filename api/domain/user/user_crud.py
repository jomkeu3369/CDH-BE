
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from api.domain.user.user_schema import UserCreate
from api.models.tasks import UserInfo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(db: AsyncSession, user_create: UserCreate):
    db_user = UserInfo(nickname=user_create.username,
                   pwd=pwd_context.hash(user_create.password1),
                   email=user_create.email,
                   gender=user_create.gender)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

async def get_existing_user(db: AsyncSession, user_create: UserCreate):
    result: Result = await db.execute(
        select(UserInfo).filter(
            (UserInfo.nickname == user_create.username) |
            (UserInfo.email == user_create.email)
        )
    )
    return result.scalars().all()

async def get_user(db: AsyncSession, username: str) -> UserInfo:
    result : Result = await db.execute(select(UserInfo).filter(UserInfo.nickname == username))
    return result.scalar_one_or_none()

async def get_user_by_userid(db: AsyncSession, user_id: int) -> UserInfo:
    result : Result = await db.execute(select(UserInfo).filter(UserInfo.user_id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> UserInfo:
    result : Result = await db.execute(select(UserInfo).filter(UserInfo.email == email))
    return result.scalar_one_or_none()


