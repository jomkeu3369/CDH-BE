from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os

router = APIRouter()
router.mount("/static", StaticFiles(directory=os.path.join("api", "static")), name="static")

templates = Jinja2Templates(directory=os.path.join("api", "templates"))

@router.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("index.html",{"request":request})
