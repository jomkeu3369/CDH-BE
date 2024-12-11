from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.domain.langchain.langchain_model import graph
from api.domain.user import user_router
from api.models import ORM
from api.domain.note import note_crud
from api.domain.erd import erd_crud
from api.domain.api import api_crud
from api.domain.langchain import langchian_crud, langchain_DB
from api.database import get_db

from typing import List
import os


router = APIRouter(
    prefix="/stack/api/v1",
    tags=["langchain"]
)

@router.get("/chain/{note_id}")
async def invoke_langchain(note_id: int, db:AsyncSession = Depends(get_db), 
                           current_user: ORM.UserInfo = Depends(user_router.get_current_user)):

    note_data = await note_crud.get_note(db=db, note_id=note_id)
    if note_data is None:
        raise HTTPException(status_code=400, detail=f"note 데이터를 찾을 수 없습니다.")
    
    if note_data.user_id != current_user.user_id:
        raise HTTPException(status_code=400, detail=f"권한이 없습니다.")

    api_data = await api_crud.get_api(db=db, note_id=note_id, api_id=note_data.api.api_id)
    erd_data = await erd_crud.get_uploaded_erd(note_id=note_id, erd_id=note_data.erd.erd_id)
    # erd_data = await erd_crud.get_erd(db=db, note_id=note_id, erd_id=note_data.erd.erd_id)

    print(f"erd_data: {erd_data}")
    result = await graph.ainvoke(input={
        "counter": 0,
        "note_id": note_data.note_id,
        "user_id": current_user.user_id,
        "original_query": note_data.content,
        "optimize_query": None,
        "generation": None,
        "api_query": api_data.content,
        "erd_query": erd_data,
        "self_rag": False,
        "self_rag_counter": 0,
        "vector_store_context": [],
        "web_search_context": []
    })
    
    return result.get("generation", None)

async def is_allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in {".pdf", ".csv", ".txt"}

@router.post("/notes/file/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def langchain_upload_files(note_id: int, files: List[UploadFile] = File(...),
                                 current_user: ORM.UserInfo = Depends(user_router.get_current_user)):
    for file in files:
        if not (await is_allowed_file(file.filename)):
            raise HTTPException(status_code=400, detail=f"'{file.filename}'은 허용되지 않는 파일 형식입니다.")
        
        await langchian_crud.upload_file(user=current_user, note_id=note_id, file=file)

@router.post("/file/test/{note_id}")
async def langchain_upload_files_test(note_id: int, message: str,
                                 current_user: ORM.UserInfo = Depends(user_router.get_current_user)):
    
    VectorStore_retriever = langchain_DB.db.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 4,
            "filter": {"user_id": current_user.user_id, "note_id": note_id}
        },
    )

    result = await VectorStore_retriever.ainvoke(input=message)
    return result