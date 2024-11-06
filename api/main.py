from fastapi import FastAPI
from api.domain.user import user_router
from api.domain.setting import setting_router
from api.domain.note import note_router
from starlette.middleware.cors import CORSMiddleware

from langserve import add_routes
from api.domain.langchain.langchain_models import model
from api.domain.langchain.langchain_main_model import chain

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

# langserve
add_routes(app, model, path="/openai")
add_routes(app, chain, path="/chain")