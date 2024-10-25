from fastapi import FastAPI
from api.domain.user import user_router
from api.domain.setting import setting_router
from api.domain.note import note_router
from starlette.middleware.cors import CORSMiddleware

import os

app = FastAPI()

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

app.include_router(user_router.router)
app.include_router(setting_router.router)
app.include_router(note_router.router)