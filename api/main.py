from fastapi import FastAPI, Depends, File, UploadFile
from starlette.middleware.cors import CORSMiddleware

from api.domain.user import user_router
from api.domain.setting import setting_router
from api.domain.note import note_router
from api.domain.langchain import langchain_router
from api.domain.erd import erd_router
from api.domain.api import api_router
from api.domain.langchain.langchain_models import model
from api.domain.langchain.langchain_main_model import chain

from langserve import add_routes
import os

app = FastAPI(
  title="PBL server for J3 Together teams",
  version="1.0",
  description="캡스톤 디자인 H조 백엔드 서버입니다.",
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/version", tags=["root"])
async def get_version():
    return {"version": os.getenv("version")}

@app.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}

@app.post("/uploadfile/")   
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}


# FastAPI
app.include_router(user_router.router)
app.include_router(setting_router.router)
app.include_router(note_router.router)
app.include_router(langchain_router.router)
app.include_router(erd_router.router)
app.include_router(api_router.router)


# langserve
# add_routes(app, model, path="/stack/api/v1/openai", dependencies=[Depends(user_router.get_current_user)])
# add_routes(app, chain, path="/chain", dependencies=[Depends(user_router.get_current_user)])
add_routes(app, chain, path="/chain", dependencies=[Depends(user_router.get_current_user)])   