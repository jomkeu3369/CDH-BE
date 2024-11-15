import os
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests

from fastapi import HTTPException
from api.domain.user.user_schema import SocialMember, SnsType

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

async def auth_google(code: str):
    try:
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        token_headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data, headers=token_headers)
        
        if response.status_code == 200:
            token_data = response.json()
            id_info = id_token.verify_oauth2_token(token_data["id_token"], requests.Request(), GOOGLE_CLIENT_ID, clock_skew_in_seconds=10)
            
            return SocialMember(
                token=token_data["id_token"],
                email=id_info["email"],
                nickname=id_info["name"],
                provider_id=id_info["sub"],
                provider=SnsType.google,
            )
        return None
    
    except Exception as e:
        raise Exception(f"Google OAuth error: {str(e)}")

async def verify_token(token:str):
    id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID, clock_skew_in_seconds=10)
    return id_info