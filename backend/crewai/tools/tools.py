import json 
import logging
import random
import time
from typing import Dict, List, Union

from crewai.tools import tool
from crewai_tools import SeleniumScrapingTool
from pydantic import ValidationError

from backend.crewai.db.insert_affiliate_stores import insert_stores
from backend.crewai.db.insert_product_list import insert_products
from backend.crewai.schemas.affiliate_store import AffiliateStoreCreate
from backend.crewai.schemas.product import ProductCreate
# Importe o logger
from backend.crewai.tools.debug_logger import setup_logger

# Configure o nível do logger
LOG_LEVEL = logging.DEBUG  # Altere para logging.INFO para desativar debug
logger = setup_logger(level=LOG_LEVEL)


@tool("Read a website content")
def read_website_content(website_url: str, css_element: str, max_attempts: int = 2) -> str:
    """
    Lê o conteúdo de um site usando Selenium com múltiplas tentativas em caso de falha de sessao.
    Parâmetros:
    - website_url: URL do site a ser acessado
    - css_element: seletor CSS para extrair dados
    - max_attempts: número de tentativas em caso de erro (default: 2)
    """
    logger.debug(f"[read_website_content] Parâmetros recebidos: {locals()}")

    errors = []

    for attempt in range(1, max_attempts + 1):
        try:
            tool = SeleniumScrapingTool(
                website_url=website_url,
                css_element=css_element
            )
            result = tool.run()
            logger.info("[read_website_content] Conteúdo extraído com sucesso.")
            return result 
        except Exception as e:
            error_msg = str(e)
            errors.append(f"[Tentativa {attempt}] {error_msg}")
            logger.error(f"Erro na tentativa {attempt}: {error_msg}", exc_info=True)

            if "invalid session id" in error_msg.lower():
                time.sleep(random.uniform(0, 3))  

    logger.warning("Todas as tentativas falharam.")
    return f"Falha após {max_attempts} tentativas. Erros:\n" + "\n".join(errors)


@tool('InsertAffiliateStoresTool')
def insert_affiliate_stores_tool(stores: List[Dict]) -> str:
    """
    Itera sobre uma lista de lojas afiliadas e insere cada uma no banco de dados.
    Espera que cada item siga o schema AffiliateStoreCreate.
    """
    logger.debug(f"[insert_affiliate_stores_tool] Recebido: {stores}")

    success_count = 0
    errors = []

    for i, store in enumerate(stores, 1):
        try:
            validated_store = AffiliateStoreCreate(**store)
            insert_stores([validated_store.dict()])
            success_count += 1
        except ValidationError as ve:
            errors.append(f"[{i}] Validaçao falhou: {ve}")
        except Exception as e:
            errors.append(f"[{i}] Erro de inserçao: {e}")

    result = f"{success_count} lojas afiliadas inseridas com sucesso."
    if errors:
        result += f"\n{len(errors)} falharam:\n" + "\n".join(errors)
    return result


@tool('InsertProductsTool')
def insert_product_list_tool(products_input: Union[str, List[Dict], Dict]) -> str:
    """
    Itera sobre uma lista de produtos e insere cada um no banco de dados.
    Suporta entrada como lista de dicionários, dicionário com chave 'products_input',
    ou string JSON equivalente.
    """
    logger.debug(f"[insert_product_list_tool] products_input: {products_input}")

    try:
        # Se for string, fazer o parsing
        if isinstance(products_input, str):
            products_input = json.loads(products_input)

        # Extrair lista de produtos corretamente
        if isinstance(products_input, dict) and 'products_input' in products_input:
            products = products_input['products_input']
        elif isinstance(products_input, list):
            products = products_input
        else:
            return f"Erro: entrada nao reconhecida. Tipo: {type(products_input)}"

    except Exception as e:
        return f"Erro ao processar entrada JSON: {e}"

    success_count = 0
    errors = []

    for i, product in enumerate(products, 1):
        try:
            validated_product = ProductCreate(**product)
            insert_products([validated_product.dict()])
            success_count += 1
        except ValidationError as ve:
            errors.append(f"[{i}] Falha na validaçao: {ve}")
        except Exception as e:
            errors.append(f"[{i}] Erro ao inserir no banco: {e}")

    result = f"{success_count} produtos inseridos com sucesso."
    if errors:
        result += f"\n{len(errors)} produtos falharam:\n" + "\n".join(errors)

    return result