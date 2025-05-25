from typing import Dict, List
from crewai.tools import tool

from pydantic import ValidationError
from backend.crewai.db.insert_affiliate_stores import insert_stores
from backend.crewai.schemas.affiliate_store import AffiliateStoreCreate

@tool('InsertAffiliateStoresTool')
def insert_affiliate_stores_tool(stores: List[Dict]) -> str:
    """
    Itera sobre uma lista de lojas afiliadas e insere cada uma no banco de dados.
    Espera que cada item siga o schema AffiliateStoreCreate.
    """
    success_count = 0
    errors = []

    for i, store in enumerate(stores, start=1):
        try:
            # Validação com o schema AffiliateStoreCreate
            validated_store = AffiliateStoreCreate(**store)
            insert_stores([validated_store.dict()])
            success_count += 1
        except ValidationError as ve:
            errors.append(f"Validação falhou na loja #{i} ({store.get('name', 'sem nome')}): {ve}")
        except Exception as e:
            errors.append(f"Erro de inserção na loja #{i} ({store.get('name', 'sem nome')}): {e}")

    result = f"{success_count} lojas afiliadas inseridas com sucesso."
    if errors:
        result += f" {len(errors)} falharam:\n" + "\n".join(errors)

    return result


# @tool('InsertAffiliateStoresTool')
# def insert_affiliate_stores_tool(stores: List[Dict]) -> str:
#     """
#     Insert a list of affiliate stores into the database.
#     Expects each item to match the AffiliateStoreCreate schema.
#     """
#     try:
#         inserted = insert_affiliate_stores(stores)
#         return f"{len(inserted)} affiliate stores successfully inserted."
#     except Exception as e:
#         return f"Failed to insert affiliate stores: {e}"


# @tool('InsertProductsTool')
# def insert_products_tool(products_by_store: Dict[str, List[Dict]]) -> str:
#     """
#     Insert products grouped by store into the database.
#     The key must be the store name, and the value must be a list of products following ProductCreate schema.
#     """
#     total_inserted = 0
#     try:
#         for store_name, products in products_by_store.items():
#             inserted = insert_products(products_data=products, affiliate_store_name=store_name)
#             total_inserted += len(inserted)
#         return f"{total_inserted} products inserted across {len(products_by_store)} stores."
#     except Exception as e:
#         return f"Failed to insert products: {e}"
