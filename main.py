from fastapi import FastAPI
from typing import Union

app = FastAPI()

@app.get('/')
async def get_model():
    return {"text": 1}