from fastapi import FastAPI
from api.domain.user import user_router
import os

app = FastAPI()

@app.get("/version")
async def get_version():
    return {"version": os.getenv("version")}

app.include_router(user_router.router)
