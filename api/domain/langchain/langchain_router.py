from fastapi import APIRouter, Depends

from api.domain.langchain.langchain_main_model import chain
from api.domain.user import user_router
from api.models import ORM

router = APIRouter()

@router.post("/langchain/invoke")
async def invoke_langchain(data: dict, current_user: ORM.UserInfo = Depends(user_router.get_current_user)):
    result = await chain.ainvoke(data)
    return result