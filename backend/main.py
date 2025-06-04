# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.endpoints import router

app = FastAPI()

# Libera acesso de todas as origens durante desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- Pode restringir para ['http://localhost:5173']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
