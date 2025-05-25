"""
Module for inserting affiliate stores into the database.
Provides functions for validating and persisting new affiliate stores.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from .session import get_db
from ..models.affiliate_store import AffiliateStore


def insert_store(store_data: Dict[str, Any], db: Session) -> AffiliateStore:
    """
    Inserts a single affiliate store into the database.
    Args:
        store_data: Dictionary with the store data.
        db: SQLAlchemy session.
    Returns:
        AffiliateStore: The inserted store instance.
    """
    name = store_data.get("name")
    platform = store_data.get("platform")
    active = store_data.get("active", True)
    api_credentials = store_data.get("api_credentials", {})

    existing_store = db.query(AffiliateStore).filter(
        AffiliateStore.name == name,
        AffiliateStore.platform == platform
    ).first()

    if existing_store:
        # Update existing store
        existing_store.active = active
        existing_store.api_credentials = api_credentials
        db.commit()
        db.refresh(existing_store)
        return existing_store

    # Insert new store
    new_store = AffiliateStore(
        name=name,
        platform=platform,
        active=active,
        api_credentials=api_credentials
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store


def insert_stores(stores_data: List[Dict[str, Any]], db_session: Optional[Session] = None) -> List[AffiliateStore]:
    """
    Inserts multiple affiliate stores into the database.

    Args:
        stores_data: List of dictionaries containing store data.
        db_session: Optional existing database session.

    Returns:
        List[AffiliateStore]: List of inserted store instances.
    """
    if db_session:
        return _insert_with_session(stores_data, db_session)
    else:
        db = next(get_db())
        try:
            return _insert_with_session(stores_data, db)
        finally:
            db.close()


def _insert_with_session(stores_data: List[Dict[str, Any]], db: Session) -> List[AffiliateStore]:
    inserted = []
    for store_data in stores_data:
        store = insert_store(store_data, db)
        inserted.append(store)
    return inserted
