from fastapi import FastAPI
from api.routers import tasks

app = FastAPI(redoc_url=None)
app.include_router(tasks.router)
