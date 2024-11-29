from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.database import get_db
from api.domain.user import user_router
from api.models import ORM

from api.domain.note import note_crud, note_schema
from api.domain.erd import erd_crud, erd_schema
from api.domain.api import api_crud, api_schema

router = APIRouter(
    prefix="/stack/api/v1",
)

# 팀 스페이스 조회

async def 

# 팀 스페이스 전환