from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.database import get_db
from api.domain.user import user_router
from api.models import ORM

from api.domain.note import note_crud, note_schema
from api.domain.erd import erd_crud, erd_schema
from api.domain.api import api_crud, api_schema
from api.domain.teamspace import teamspace_crud

router = APIRouter(
    prefix="/stack/api/v1",
)

# 전체 노트 조회
@router.get("/notes", response_model=note_schema.NoteList, tags=["notes"])
async def note_list(db: AsyncSession = Depends(get_db), page: int = 0, size: int = 10, keyword: str = '',
                    current_user: ORM.UserInfo = Depends(user_router.get_current_user)):
    total, _note_list = await note_crud.search_notes(db, user=current_user, skip=page * size, limit=size, keyword=keyword)

    note_list_with_ids = []
    for note in _note_list:
        erd = await erd_crud.get_erd_by_note_id(db, note_id=note.note_id)
        api = await api_crud.get_api_by_note_id(db, note_id=note.note_id)
        
        group = None
        if note.teamspace_id is not None:
            group = await teamspace_crud.get_teamspace(db=db, teamspcae_id=note.teamspace_id)
        
        note_list_with_ids.append({
            "note_id": note.note_id,
            "user_id": note.user_id,
            "content": note.content,
            "teamspace_id": note.teamspace_id,
            "member": group.members if group is not None else [],
            "title": note.title,
            "is_teamspace": True if note.teamspace_id is not None else False,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
            "erd_id": erd.erd_id if erd else None,
            "api_id": api.api_id if api else None
        })

    return {
        "total": total,
        "note_list": note_list_with_ids
    }

# 노트 조회
@router.get("/notes/{note_id}", response_model=note_schema.NoteResponse, tags=["notes"])
async def get_note(note_id: int, db: AsyncSession = Depends(get_db),
                   current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    note = await note_crud.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    if note.user_id != current_user.user_id:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="권한이 없습니다.")

    group = None
    if note.teamspace_id is not None:
        group = await teamspace_crud.get_teamspace(db=db, teamspcae_id=note.teamspace_id)

    return note_schema.NoteResponse(
        note_id=note.note_id,
        user_id=note.user_id,
        title=note.title,
        content=note.content,
        is_teamspace=True if note.teamspace_id is not None else False,
        created_at=note.created_at,
        member=group.members if group is not None else [],
        updated_at=note.updated_at
    )

# 노트 생성
@router.post("/note", response_model=note_schema.NoteCreateSuccess, tags=["notes"])
async def note_create(_note_create: note_schema.NoteCreate, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    note = await note_crud.create_note(db=db, note_create=_note_create, user=current_user)
    erd = await erd_crud.create_erd(db=db, erd_create=erd_schema.ERDCreate(note_id=note.note_id, user_id=current_user.user_id))
    api = await api_crud.create_api(db=db, api_create=api_schema.APICreate(note_id=note.note_id, user_id=current_user.user_id))
    
    return note_schema.NoteCreateSuccess(
        user_id=current_user.user_id,
        note_id=note.note_id,
        api_id=api.api_id,
        erd_id=erd.erd_id
    )

# 노트 업데이트
@router.patch("/notes/{note_id}", status_code=status.HTTP_200_OK, tags=["notes"])
async def note_update(note_id:int, _note_update: note_schema.NoteUpdate, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    db_note = await note_crud.get_note(db, note_id=note_id)
    if not db_note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    if current_user.user_id != db_note.user_info.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    
    await note_crud.update_note(db=db, db_note=db_note, note_update=_note_update)
    update_note = await note_crud.get_note(db, note_id=note_id)
    return update_note

# 노트 삭제
@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["notes"])
async def note_delete(note_id:int, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    db_note = await note_crud.get_note(db, note_id=note_id)
    if not db_note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    if current_user.user_id != db_note.user_info.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    
    await note_crud.delete_note(db=db, db_note=db_note)
