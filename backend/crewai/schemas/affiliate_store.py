# app/schemas/affiliate_store.py
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class AffiliateStoreBase(BaseModel):
    name: str
    platform: str
    active: bool = True
    url: Optional[str] 

class AffiliateStoreCreate(AffiliateStoreBase):
    api_credentials: Dict[str, str] = Field(..., description="API credentials for the platform")

class AffiliateStoreUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    active: Optional[bool] = None
    url: Optional[str] = None
    api_credentials: Optional[Dict[str, str]] = None

class AffiliateStoreInDB(AffiliateStoreBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True