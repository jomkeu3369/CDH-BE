
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from api.domain.setting.setting_schema import settingCreate
from api.models.tasks import UserInfo, Settings

async def get_setting(db:AsyncSession, user_id:int):
    result : Result = await db.execute(select(Settings).filter(Settings.user_id == user_id))
    return result.scalar_one_or_none()

async def create_setting(db: AsyncSession, user:UserInfo):
    try:
        db_setting = Settings(user_id=user.user_id, theme="dark", font_size=17)
        db.add(db_setting)
        await db.commit()
        await db.refresh(db_setting)
        print(f"create_setting 생성 완료")
    except Exception as e:
        print(f"create_setting 오류 : {e}")

async def update_setting(db: AsyncSession, create:settingCreate, original: Settings) -> Settings:
    original.theme = create.theme
    original.font_size = original.font_size
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original

