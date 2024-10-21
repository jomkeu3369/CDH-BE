from fastapi import FastAPI
from api.domain.user import user_router
from api.domain.setting import setting_router
from api.domain.note import note_router

import os

app = FastAPI()

@app.get("/version", tags=["root"])
async def get_version():
    return {"version": os.getenv("version")}

app.include_router(user_router.router)
app.include_router(setting_router.router)
app.include_router(note_router.router)