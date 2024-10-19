from datetime import timedelta, datetime
import os

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.database import get_db
from api.domain.user import user_crud, user_schema
from api.domain.user.user_crud import pwd_context
from api.domain.setting import setting_crud

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/stack/api/v1/login")

router = APIRouter(
    prefix="/stack/api/v1",
)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def user_create(_user_create: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.")
    await user_crud.create_user(db=db, user_create=_user_create)
    
    create_user = await user_crud.get_user(db=db, username=_user_create.username)
    await setting_crud.create_setting(db=db, user=create_user)

    create_user = await user_crud.get_user(db=db, username=_user_create.username)
    
    return {
        "user_id": create_user.user_id,
        "message": "회원가입이 완료되었습니다."
    }

@router.post("/login", response_model=user_schema.Token)
async def login_for_access_token(form_data:OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):

    user = await user_crud.get_user_by_email(db, form_data.username)
    if user is None or not pwd_context.verify(form_data.password, user.pwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못 입력되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = {    
        "sub": str(user.user_id),
        "exp": datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id
    }

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="access token의 정보가 잘못되었습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = await user_crud.get_user_by_userid(db, user_id=int(user_id))
        if user is None:
            raise credentials_exception
        return user