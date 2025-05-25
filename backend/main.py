# backend/main.py
from fastapi import FastAPI
from backend.api.endpoints import router

app = FastAPI()
app.include_router(router)
