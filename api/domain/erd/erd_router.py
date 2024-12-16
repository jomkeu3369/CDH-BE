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

router = APIRouter(
    prefix="/stack/api/v1",
)

# ERD 조회
@router.get("/erd/{note_id}/{erd_id}", tags=["erds"])
async def get_erd(note_id: int, erd_id: int, db: AsyncSession = Depends(get_db),
                  current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    
    note = await note_crud.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    is_used = await note_crud.is_use(db, note_id, current_user.user_id)
    if not is_used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="권한이 없습니다.")

    erd = await erd_crud.get_uploaded_erd(note_id, erd_id)
    return FileResponse(erd)

    
# ERD 업로드
@router.post("/erdupload/{note_id}/{erd_id}", tags=["erds"])
async def upload_erd(note_id: int, erd_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db),
                    current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    
    note = await note_crud.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    is_used = await note_crud.is_use(db, note_id, current_user.user_id)
    if not is_used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="권한이 없습니다.")
    
    await erd_crud.upload_erd(file, note_id, erd_id)
    return {"message": "erd 업로드"}

    
    
