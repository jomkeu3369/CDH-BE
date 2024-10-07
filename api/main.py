from fastapi import FastAPI
from api.routers import tasks

app = FastAPI()

app.include_router(tasks.router)
