# backend/api/endpoints.py
from fastapi import APIRouter
from backend.crewai.crew_stores import executar_stores
from backend.crewai.crew_products import executar_products

router = APIRouter()

@router.get("/stores")
def run_flow(pais: str, nicho: str, periodo: str):
    resultado = executar_stores(pais, nicho, periodo)
    return resultado

@router.get("/products")
def run_flow(tema: str):
    resultado = executar_products(tema)
    return resultado
