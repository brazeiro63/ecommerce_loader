# backend/api/endpoints.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session

from backend.crewai.crew_products import scrape_store_products
from backend.crewai.crew_stores import discover_stores
from backend.crewai.db.session import get_db
from backend.crewai.models.affiliate_store import AffiliateStore
from backend.crewai.schemas.affiliate_store import AffiliateStoreInDB

router = APIRouter(prefix="/api")

@router.get("/stores", response_model=dict, status_code=200)
def discover_affiliate_stores(
    pais: str = Query(..., description="País (ex: BR)"),
    nicho: str = Query(..., description="Nicho de mercado"),
    periodo: str = Query(..., description="Período de análise")
):
    if not pais or len(pais.strip()) != 2:
        raise HTTPException(status_code=400, detail="País inválido. Deve ser uma sigla de 2 letras.")

    if not nicho:
        raise HTTPException(status_code=400,detail="Nicho de mercado inválido ou não informado.")
    
    if not periodo:
        periodo = datetime.now().year

    try:
        resultado = discover_stores(pais, nicho, periodo)
        return  resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/products/")
def scrape_products(
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
    limit: int = 100,
):
    """
    Lista as lojas afiliadas salvas no banco de dados.
    """
    stores = db.query(AffiliateStore).offset(skip).limit(limit).all()
    return stores