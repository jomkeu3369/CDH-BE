from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.database import get_db
from api.domain.user import user_router
from api.models import ORM

from api.domain.teamspace import teamspace_crud, teamspace_schema

router = APIRouter(
    prefix="/stack/api/v1",
    tags=["teamspace"]
)

# 팀 스페이스 조회
@router.post("/notes/{note_id}/switchTeamspace", response_model=teamspace_schema.TeamspaceChangeResponse)
async def teamspace_change(_teamspace_create: teamspace_schema.TeamspaceChange, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    
    group = await teamspace_crud.get_teamspace
    return teamspace_schema.TeamspaceChangeResponse(
        user_id=current_user.user_id,
        group_id=1
    )

# 팀 스페이스 전환