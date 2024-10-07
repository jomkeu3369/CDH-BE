from fastapi import APIRouter, Depends
import os

router = APIRouter()

@router.get("/version")
async def main():
    return {"version": os.getenv("version")}
