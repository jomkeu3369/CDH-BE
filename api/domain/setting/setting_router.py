from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.database import get_db
from api.domain.setting import setting_crud, setting_schema
from api.domain.user import user_crud, user_router
from api.models import tasks

router = APIRouter(
    prefix="/stack/api/v1",
)

# 설정 조회
@router.get("/setting", response_model=setting_schema.settingResponse, tags=["setting"])
async def get_setting(db: AsyncSession = Depends(get_db),
                      current_user:tasks.UserInfo = Depends(user_router.get_current_user)):
    db_setting = await setting_crud.get_setting(db, current_user.user_id)
    if db_setting is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="데이터를 찾을 수 없습니다.")
    
    return db_setting

# 세팅 업데이트
@router.put("/setting", response_model=setting_schema.settingResponse, tags=["setting"])
async def put_setting(_setting_update: setting_schema.settingCreate,
                    db: AsyncSession = Depends(get_db),
                    current_user:tasks.UserInfo = Depends(user_router.get_current_user)):
    db_setting = await setting_crud.get_setting(db, current_user.user_id)
    if db_setting is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="데이터를 찾을 수 없습니다.")
    if current_user.user_id != db_setting.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    
    await setting_crud.update_setting(db=db, create=_setting_update, original=db_setting)
    
    updated_setting = await setting_crud.get_setting(db, current_user.user_id)
    return updated_setting