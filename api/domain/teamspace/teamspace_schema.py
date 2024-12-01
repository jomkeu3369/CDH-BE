from pydantic import BaseModel
from typing import Optional, List
import datetime

class TeamspaceChangeValue(BaseModel):
    user_id: int
    nickname: str
    email: str
    joinedat: datetime.datetime

class TeamspaceChange(BaseModel):
    note_id: int

class TeamspaceChangeResponse(BaseModel):
    user_id: int
    teamspace_id: int

class TeamspaceChangeResponse(BaseModel):
    user_id: int
    teamspace_id: int

class TeamspaceResponse(BaseModel):
    teamspace_id: int
    note_id: int
    invite_id: str
    user_id: int
    members: Optional[List[TeamspaceChangeValue]]

class InviteResponse(BaseModel):
    teamspace_id: int
    members: Optional[List[TeamspaceChangeValue]]
    