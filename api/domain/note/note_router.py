from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.database import get_db
from api.domain.setting import setting_crud, setting_schema
from api.domain.user import user_crud, user_router
from api.models import ORM

from api.domain.note import note_crud, note_schema

router = APIRouter(
    prefix="/stack/api/v1",
)

# 전체 노트 조회
@router.get("/notes", response_model=note_schema.NoteList, tags=["notes"])
async def note_list(db: note_schema = Depends(get_db), page: int = 0, size: int = 10, keyword: str = '',
                    current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    total, _note_list = await note_crud.search_notes(db, user=current_user, skip=page * size, limit=size, keyword=keyword)
    return {
        'total': total,
        'note_list': _note_list
    }

# 노트 조회
@router.get("/notes/{note_id}", response_model=note_schema.Notes, tags=["notes"])
async def get_note(note_id: int, db: AsyncSession = Depends(get_db),
                   current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    note = await note_crud.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    if note.user_id != current_user.user_id:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="권한이 없습니다.")
    return note

# 노트 생성
@router.post("/note", status_code=status.HTTP_204_NO_CONTENT, tags=["notes"])
async def note_create(_note_create: note_schema.NoteCreate, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    await note_crud.create_note(db=db, note_create=_note_create, user=current_user)

# 노트 업데이트
@router.patch("/notes/update", status_code=status.HTTP_200_OK, tags=["notes"])
async def note_update(_note_update: note_schema.NoteUpdate, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    db_note = await note_crud.get_note(db, note_id=_note_update.note_id)
    if not db_note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    if current_user.user_id != db_note.user_info.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    
    await note_crud.update_note(db=db, db_note=db_note, note_update=_note_update)
    update_note = await note_crud.get_note(db, note_id=_note_update.note_id)
    return update_note


# 노트 삭제
@router.delete("/notes/delete", status_code=status.HTTP_204_NO_CONTENT, tags=["notes"])
async def note_delete(_note_delete: note_schema.NoteDelete, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    db_note = await note_crud.get_note(db, note_id=_note_delete.note_id)
    if not db_note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    if current_user.user_id != db_note.user_info.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    
    await note_crud.delete_note(db=db, db_note=db_note)
