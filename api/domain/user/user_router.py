from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status
from starlette.config import Config

from api.database import get_db
from api.domain.user import user_crud, user_schema
from api.domain.user.user_crud import pwd_context

config = Config('.env')
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "b4d61f0557fd996c89cc778ae61c4867b88d0152fd8b5158267644e1097f9551"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/stack/api/v1/login")

router = APIRouter(
    prefix="/stack/api/v1",
)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = await user_crud.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.")
    await user_crud.create_user(db=db, user_create=_user_create)
    
    create_user = await user_crud.get_user(db, _user_create.username)
    return {
        "user_id": create_user.user_id,
        "message": "회원가입이 완료되었습니다."
    }

@router.post("/login", response_model=user_schema.Token)
async def login_for_access_token(form_data:user_schema.LoginRequest, db: Session = Depends(get_db)):

    user = await user_crud.get_user_by_email(db, form_data.email)
    if user is None or not pwd_context.verify(form_data.password, user.pwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못 입력되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = {    
        "sub": user.nickname,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "token": access_token,
        "user_id": user.user_id
    }


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = await user_crud.get_user(db, username=username)
        if user is None:
            raise credentials_exception
        return user