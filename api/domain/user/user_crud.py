
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session

from api.domain.user.user_schema import UserCreate
from api.models.tasks import UserInfo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(db: Session, user_create: UserCreate):
    db_user = UserInfo(nickname=user_create.username,
                   pwd=pwd_context.hash(user_create.password1),
                   email=user_create.email,
                   gender=user_create.gender)
    db.add(db_user)
    await db.commit()


async def get_existing_user(db: Session, user_create: UserCreate):
    result: Result = await db.execute(
        select(UserInfo).filter(
            (UserInfo.nickname == user_create.username) |
            (UserInfo.email == user_create.email)
        )
    )
    return result.scalars().all()


async def get_user(db: Session, username: str):
    result : Result = await db.execute(select(UserInfo).filter(UserInfo.nickname == username))
    return result.scalar_one()

async def get_user_by_email(db: Session, email: str):
    result : Result = await db.execute(select(UserInfo).filter(UserInfo.email == email))
    return result.scalar_one()


