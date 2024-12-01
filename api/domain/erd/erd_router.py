from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi.responses import FileResponse

from api.database import get_db
from api.domain.note import note_crud
from api.domain.erd import erd_schema, erd_crud
from api.domain.user import user_router
from api.models import ORM
import os

router = APIRouter(
    prefix="/stack/api/v1",
)

UPLOAD_DIR = "erd_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ERD 조회
@router.get("/stack/api/v1/erd/{note_id}/{erd_id}", tags=["erds"])
async def get_erd(note_id: int, erd_id: int, db: AsyncSession = Depends(get_db),
                  current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    
    note = await note_crud.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    if note.user_id != current_user.user_id:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="권한이 없습니다.")

    file_path = os.path.join(UPLOAD_DIR, f"note_{note_id}_erd_{erd_id}.png")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")

    return FileResponse(file_path)

# @router.get("/erd/{note_id}/{erd_id}", response_model=erd_schema.ERDs, tags=["erds"])
# async def get_erd(note_id: int, erd_id:int, db: AsyncSession = Depends(get_db),
#                    current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
#     erd = await erd_crud.get_erd(db, note_id=note_id, erd_id=erd_id)
#     if not erd:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="데이터를 찾을 수 없습니다.")
    
#     note = await note_crud.get_note(db, note_id=erd.note_id)
#     if not note:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="데이터를 찾을 수 없습니다.")

#     if note.user_id != current_user.user_id:
#          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="권한이 없습니다.")
#     return erd

# ERD 업로드
@router.post("/stack/api/v1/erdupload/{note_id}/{erd_id}", tags=["erds"])
async def upload_erd(note_id: int, erd_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db),
                    current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    
    note = await note_crud.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    if note.user_id != current_user.user_id:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="권한이 없습니다.")

    file_path = os.path.join(UPLOAD_DIR, f"note_{note_id}_erd_{erd_id}.png")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"message": "erd 업로드"}

# ERD 수정
@router.put("/erdupload/{note_id}/{erd_id}", response_model=erd_schema.ERDs, tags=["erds"])
async def erd_update(note_id: int, erd_id:int, _erd_update: erd_schema.ERDUpdate, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    db_erd = await erd_crud.get_erd(db, note_id=note_id, erd_id=erd_id)
    if not db_erd:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    note = await note_crud.get_note(db, note_id=db_erd.note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")

    if current_user.user_id != note.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    
    await erd_crud.update_erd(db=db, db_erd=db_erd, erd_update=_erd_update)
    update_erd = await erd_crud.get_erd(db, note_id=note_id, erd_id=erd_id)
    return update_erd

# ERD 삭제
@router.delete("/erd/{note_id}/{erd_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["erds"])
async def erd_delete(note_id:int, erd_id:int, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    db_erd = await erd_crud.get_erd(db, note_id=note_id, erd_id=erd_id)
    if not db_erd:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    note = await note_crud.get_note(db, note_id=db_erd.note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    if current_user.user_id != note.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    
    await erd_crud.delete_erd(db=db, db_erd=db_erd)
