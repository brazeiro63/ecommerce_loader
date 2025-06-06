import json 
import time
from typing import Dict, List, Union

from crewai.tools import tool
from crewai_tools import SeleniumScrapingTool
from pydantic import ValidationError

from backend.crewai.db.insert_affiliate_stores import insert_stores
from backend.crewai.db.insert_product_list import insert_products
from backend.crewai.schemas.affiliate_store import AffiliateStoreCreate
from backend.crewai.schemas.product import ProductCreate


@tool("Read a website content")
def read_website_content(website_url: str, css_element: str, max_attempts: int = 3) -> str:
    """
    Lê o conteúdo de um site usando Selenium com múltiplas tentativas em caso de falha de sessao.

    Parâmetros:
    - website_url: URL do site a ser acessado
    - css_element: seletor CSS para extrair dados
    - max_attempts: número de tentativas em caso de erro (default: 3)
    """
    errors = []

    for attempt in range(1, max_attempts + 1):
        try:
            tool = SeleniumScrapingTool(
                website_url=website_url,
                css_element=css_element
            )
            result = tool.run()
            return result  # ✅ sucesso
        except Exception as e:
            error_msg = str(e)
            errors.append(f"[Tentativa {attempt}] {error_msg}")

            if "invalid session id" in error_msg.lower():
                time.sleep(1)  # ⏱️ pequena espera antes da próxima tentativa

    # ❌ todas as tentativas falharam
    return f"Falha após {max_attempts} tentativas. Erros:\n" + "\n".join(errors)


@tool('InsertAffiliateStoresTool')
def insert_affiliate_stores_tool(stores: List[Dict]) -> str:
    """
    Itera sobre uma lista de lojas afiliadas e insere cada uma no banco de dados.
    Espera que cada item siga o schema AffiliateStoreCreate.
    """
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