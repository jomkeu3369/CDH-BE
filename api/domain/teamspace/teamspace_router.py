from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.database import get_db
from api.domain.user import user_router, user_crud
from api.models import ORM

from api.domain.teamspace import teamspace_crud, teamspace_schema
from api.domain.note import note_crud

router = APIRouter(
    prefix="/stack/api/v1",
    tags=["teamspace"]
)

# 팀 스페이스 조회
@router.get("/teamspace/{group_id}", response_model=teamspace_schema.TeamspaceResponse)
async def get_note(group_id: int, db: AsyncSession = Depends(get_db),
                   current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    group = await teamspace_crud.get_teamspace(db=db, teamspcae_id=group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    
    note = await note_crud.get_note_with_teamspaceID(db, teamspace_id=group.id)
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")

    return teamspace_schema.TeamspaceResponse(
        teamspace_id=group.id,
        note_id=note.note_id,
        invite_id=group.invite_id,
        user_id=group.user_id,
        members=group.members
    )

# 팀 스페이스 전환
@router.post("/notes/{note_id}/switchTeamspace", response_model=teamspace_schema.TeamspaceChangeResponse)
async def teamspace_change(_teamspace_create: teamspace_schema.TeamspaceChange, db: AsyncSession = Depends(get_db),
                          current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    
    note = await note_crud.get_note(db, note_id=_teamspace_create.note_id)
    
    if not note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    if current_user.user_id != note.user_info.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="생성 권한이 없습니다.")
    if note.teamspace_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="팀 스페이스를 중복해서 생성할 수 없습니다.")
    group = await teamspace_crud.create_teamspace(db=db, note=note ,user=current_user)
    return teamspace_schema.TeamspaceChangeResponse(
        user_id=current_user.user_id,
        teamspace_id=group.id
    )

@router.post("/notes/{group_id}/invite", response_model=teamspace_schema.InviteResponse, status_code=status.HTTP_200_OK)
async def invite_member_to_group(group_id: int, nickname: str, db: AsyncSession = Depends(get_db),
                                 current_user:ORM.UserInfo = Depends(user_router.get_current_user)):
    
    user = await user_crud.get_user(db, username=nickname)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="닉네임에 해당하는 사용자를 찾을 수 없습니다."
        )

    group = await teamspace_crud.get_teamspace(db, teamspcae_id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 팀스페이스를 찾을 수 없습니다."
        )

    if any(member["user_id"] == user.user_id for member in (group.members or [])):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 사용자는 이미 그룹의 멤버입니다."
        )

    if len(group.members or []) >= 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹에 더 이상 멤버를 추가할 수 없습니다. 최대 4명까지 참여 가능합니다."
        )

    updated_group = await teamspace_crud.add_member_to_group(db, group, user)

    return {"teamspace_id": group.id, "members": updated_group.members}