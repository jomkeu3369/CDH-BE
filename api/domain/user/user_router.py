from datetime import timedelta, datetime
from typing import Annotated
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer 
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from api.database import get_db
from api.domain.user import user_crud, user_schema, user_login_handler
from api.domain.user.user_crud import pwd_context
from api.domain.setting import setting_crud

# google Oauth 
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPE = "openid profile email"

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/stack/api/v1/login/email")
google_oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=GOOGLE_AUTH_URI,
    tokenUrl=GOOGLE_TOKEN_URI,
    scopes={"email": "email", "profile": "profile", "openid": "openid"}
)

class AuthDependencies:
    def __init__(
        self,
        dep1: Annotated[str, Depends(google_oauth2_scheme)],
        dep2: Annotated[str, Depends(oauth2_scheme)]
    ):
        self.dep1 = dep1
        self.dep2 = dep2

router = APIRouter(
    prefix="/stack/api/v1",
)

@router.post("/signup", status_code=status.HTTP_201_CREATED, tags=["login"])
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

@router.post("/login/email", response_model=user_schema.Token, tags=["login"])
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

    return user_schema.Token(
        user_id=user.user_id,
        access_token=access_token,
        token_type="bearer"
    )

@router.get("/login/{provider}", tags=["login"])
async def login(provider: user_schema.SnsType):
    match provider:
        case "google":
            return RedirectResponse(
                f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope={GOOGLE_SCOPE}"
            )
        case _:
            raise HTTPException(status_code=400, detail="Invalid provider")

@router.get("/auth/callback/{provider}", tags=["login"])
async def auth_callback(provider: user_schema.SnsType, code: str, db: AsyncSession = Depends(get_db)):
    match provider:
        case "google":
            auth_google:user_schema.SocialMember = await user_login_handler.auth_google(code)
            if auth_google is not None:
                user_sub = auth_google.provider_id
                user_data = await user_crud.get_user_by_sub(db, user_sub)

                if not user_data:
                    await user_crud.create_social_user(db, auth_google) 
                user_info = await user_crud.get_user_by_sub(db, user_sub)

                data = {    
                    "sub": user_info.user_id,
                    "exp": datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
                }
                access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

                return user_schema.Token(
                    user_id=user_info.user_id,
                    access_token=access_token,
                    token_type="Bearer"
                )
            else:
                raise HTTPException(status_code=400, detail="인증 실패")
        case _:
            raise HTTPException(status_code=400, detail="Invalid provider")

async def get_current_user(token:str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    
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
        else:
            user = await user_crud.get_user_by_userid(db, user_id=int(user_id))
            if user is None:
                raise credentials_exception
            return user

    except JWTError:
        raise credentials_exception