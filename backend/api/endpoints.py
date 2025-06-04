# backend/api/endpoints.py
from typing import List

from fastapi import APIRouter, Depends, Query
from requests import Session

from backend.crewai.crew_products import scrape_store_products
from backend.crewai.crew_stores import discover_stores
from backend.crewai.db.session import get_db
from backend.crewai.models.affiliate_store import AffiliateStore
from backend.crewai.schemas.affiliate_store import AffiliateStoreInDB

router = APIRouter(prefix="/api")

@router.get("/stores")
def run_flow(pais: str, nicho: str, periodo: str):
    resultado = discover_stores(pais, nicho, periodo)
    return resultado

@router.get("/products/")
def run_flow(
    loja: str = Query(..., description="Nome da loja"),
    url: str = Query(..., description="URL da loja"),
    nicho: str = Query(..., description="Nicho a buscar"),
    quantidade: str = Query(..., description="Quantidade de produtos")
):
    resultado = scrape_store_products(
        loja_url=loja, 
        nicho_busca= nicho, 
        quantidade_produtos= quantidade
    )
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