from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import json

from api.database import get_db
from api.domain.note import note_crud
from api.domain.api import api_schema, api_crud
from api.domain.user import user_router
from api.models import ORM

router = APIRouter(
    prefix="/stack/api/v1", tags=["apis"]
)

# API 명세서 조회
@router.get("/api/{note_id}/{api_id}", response_model=api_schema.APIs)
async def get_note(note_id: int, api_id:int, db: AsyncSession = Depends(get_db),
                   current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    api = await api_crud.get_api(db, note_id=note_id, api_id=api_id)
    if not api:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    note = await note_crud.get_note(db, note_id=api.note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")

    if note.user_id != current_user.user_id:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="권한이 없습니다.")
    return api

# API 명세서 수정
@router.put("/api/{note_id}/{api_id}", response_model=api_schema.APIs)
async def api_update(note_id: int, api_id:int, _api_update: api_schema.APIUpdate, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    api = await api_crud.get_api(db, note_id=note_id, api_id=api_id)
    if not api:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    note = await note_crud.get_note(db, note_id=api.note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")

    if current_user.user_id != note.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    
    try:
        content_data = json.loads(_api_update.content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    updated_content = [
        {
            "url": entry.get("url", ""),
            "method": entry.get("method", "GET"),
            "request": entry.get("request", ""),
            "response": entry.get("response", "")
        }
    for entry in content_data
        ]

    update_data = {
        "title": _api_update.title,
        "content": updated_content 
    }

    await api_crud.update_api(db=db, db_api=api, api_update=update_data)
    update_api = await api_crud.get_api(db, note_id=note_id, api_id=api_id)
    return update_api

# API 명세서 삭제
@router.delete("/api/{note_id}/{api_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete(note_id:int, api_id:int, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    api = await api_crud.get_api(db, note_id=note_id, api_id=api_id)
    if not api:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    note = await note_crud.get_note(db, note_id=api.note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    if current_user.user_id != note.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    
    await api_crud.delete_api(db=db, db_api=api)
