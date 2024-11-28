from fastapi import FastAPI, Depends, File, UploadFile
from starlette.middleware.cors import CORSMiddleware

from api.domain.user import user_router
from api.domain.setting import setting_router
from api.domain.note import note_router
from api.domain.langchain import langchain_router
from api.domain.erd import erd_router
from api.domain.api import api_router
from api.domain.langchain.langchain_model import graph
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
add_routes(app, graph, path="/chain")   