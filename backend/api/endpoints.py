# backend/api/endpoints.py
from typing import List
from fastapi import APIRouter, Depends
from requests import Session
from backend.crewai.crew_stores import discover_stores
from backend.crewai.crew_products import discover_products
from backend.crewai.db.session import get_db
from backend.crewai.models.affiliate_store import AffiliateStore
from backend.crewai.schemas.affiliate_store import AffiliateStoreInDB

router = APIRouter()

@router.get("/stores")
def run_flow(pais: str, nicho: str, periodo: str):
    resultado = discover_stores(pais, nicho, periodo)
    return resultado

@router.get("/products")
def run_flow(loja: str):
    resultado = discover_products(loja)
    return resultado

@router.get("/list", response_model=List[AffiliateStoreInDB])
def list_affiliate_stores(
    db: Session = Depends(get_db),
    skip: int = 0, 
    limit: int = 100
):
    """
    Lista as lojas afiliadas salvas no banco de dados.
    """
    stores = db.query(AffiliateStore).offset(skip).limit(limit).all()
    return stores