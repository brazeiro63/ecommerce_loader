"""
Module for inserting products into the database.
Provides functions for validating and persisting new products.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..models.products import Product
from .session import get_db


def insert_product(product_data: Dict[str, Any], db: Session) -> Product:
    """
    Inserts a single product into the database.
    Args:
        product_data: Dictionary with the product data.
        db: SQLAlchemy session.
    Returns:
        Products: The inserted product instance.
    """
    external_id = product_data.get("external_id")
    platform = product_data.get("platform")
    title = product_data.get("title")
    description = product_data.get("description")
    price = product_data.get("price")
    sale_price = product_data.get("sale_price")
    image_url = product_data.get(["image_url"])
    product_url = product_data.get("product_url")
    category = product_data.get("category")
    brand = product_data.get("brand")
    available = product_data.get("available", True)

    existing_product = db.query(Product).filter(
        Product.title == title,
        Product.platform == platform
    ).first()

    if existing_product:
        # Update existing product
        existing_product.external_id = external_id
        existing_product.description = description
        existing_product.price = price
        existing_product.sale_price = sale_price
        existing_product.image_url = image_url
        existing_product.product_url = product_url
        existing_product.category = category
        existing_product.brand = brand
        existing_product.available = available
        db.commit()
        db.refresh(existing_product)
        return existing_product

    # Insert new product
    new_product = Product(
        title=title,
        platform=platform,
        external_id=external_id,
        description=description,
        price=price,
        sale_price=sale_price,
        image_url=image_url,
        product_url=product_url,
        category=category,
        brand=brand,
        available=available
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def insert_products(products_data: List[Dict[str, Any]], db_session: Optional[Session] = None) -> List[Product]:
    """
    Inserts multiple products into the database.

    Args:
        products_data: List of dictionaries containing product data.
        db_session: Optional existing database session.

    Returns:
        List[Products]: List of inserted product instances.
    """
    if db_session:
        return _insert_with_session(products_data, db_session)
    else:
        db = next(get_db())
        try:
            return _insert_with_session(products_data, db)
        finally:
            db.close()


def _insert_with_session(products_data: List[Dict[str, Any]], db: Session) -> List[Product]:
    inserted = []
    for product_data in products_data:
        product = insert_product(product_data, db)
        inserted.append(product)
    return inserted
