
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from api.domain.user.user_schema import UserCreate, SocialMember, SnsType
from api.models.ORM import UserInfo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(db: AsyncSession, user_create: UserCreate):
    db_user = UserInfo(nickname=user_create.username,
                   pwd=pwd_context.hash(user_create.password1),
                   email=user_create.email,
                   gender=user_create.gender,
                   provider_type=SnsType.email)
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

async def create_social_user(db: AsyncSession, user_create: SocialMember):
    nickname = user_create.nickname

    db_user = await db.execute(select(UserInfo).filter(UserInfo.nickname == nickname))
    db_user = db_user.scalars().first()

    if db_user:
        base_nickname = nickname
        count = 1
        while db_user:
            nickname = f"{base_nickname}_{count}"
            db_user = await db.execute(select(UserInfo).filter(UserInfo.nickname == nickname))
            db_user = db_user.scalars().first()
            count += 1

    db_user = UserInfo(
        nickname=nickname,
        email=user_create.email,
        provider_type=user_create.provider.name,
        provider_id=int(user_create.provider_id)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)


async def get_user(db: AsyncSession, username: str) -> UserInfo:
    result : Result = await db.execute(select(UserInfo).filter(UserInfo.nickname == username))
    return result.scalar_one_or_none()

async def get_user_by_userid(db: AsyncSession, user_id: int) -> UserInfo:
    result : Result = await db.execute(select(UserInfo).filter(UserInfo.user_id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> UserInfo:
    result : Result = await db.execute(select(UserInfo).filter(UserInfo.email == email))
    return result.scalar_one_or_none()

async def get_user_by_sub(db: AsyncSession, sub: str) -> UserInfo:
    result : Result = await db.execute(select(UserInfo).filter(UserInfo.provider_id == sub))
    return result.scalar_one_or_none()
