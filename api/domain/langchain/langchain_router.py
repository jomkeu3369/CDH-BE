from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
import os

from starlette import status
from api.domain.langchain.langchain_main_model import chain
from api.domain.user import user_router
from api.models import ORM
from api.domain.langchain import langchian_crud

router = APIRouter(
    prefix="/stack/api/v1",
    tags=["langchain"]
)

@router.post("/langchain/invoke")
async def invoke_langchain(data: dict, current_user: ORM.UserInfo = Depends(user_router.get_current_user)):
    result = await chain.ainvoke(data)
    return result

async def is_allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in {".pdf", ".csv", ".txt"}

@router.post("/notes/file/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def langchain_upload_files(note_id: int, files: List[UploadFile] = File(...),
                                 current_user: ORM.UserInfo = Depends(user_router.get_current_user)):
    for file in files:
        if not (await is_allowed_file(file.filename)):
            raise HTTPException(status_code=400, detail=f"'{file.filename}'은 허용되지 않는 파일 형식입니다.")
        
        await langchian_crud.upload_file(user=current_user, file=file)