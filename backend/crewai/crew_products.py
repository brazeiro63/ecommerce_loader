# backend/crewai/crew_product_scraper.py
import logging
from crewai import Crew, Process

from backend.crewai.agents import (
    affiliate_output_formatter_agent,
    product_data_curator_agent,
    product_database_inserter_agent,
    product_detail_extractor_agent,
    product_listing_agent,
    product_structure_analyst,
    store_navigator_agent,
    ecommerce_structure_specialist
    )
from backend.crewai.tasks import (
    analyze_scraped_html_task,
    build_pydantic_objects_task,
    clean_and_format_product_data_task,
    extract_individual_product_details_task,
    identify_product_urls_task,
    insert_scraped_products_task,
    navigate_and_search_store_task,
    identify_ecomerce_structure_task
    )

# Importe o logger
from backend.crewai.tools.debug_logger import setup_logger

# Configure o nível do logger
LOG_LEVEL = logging.DEBUG  # Altere para logging.INFO para desativar debug
logger = setup_logger(level=LOG_LEVEL)




def scrape_store_products(loja_url: str, nicho_busca: str, quantidade_produtos: int):
    """
    Cria e executa uma CrewAI para acessar o site de uma loja, buscar produtos de um nicho
    específico e extrair informações detalhadas para uma loja de afiliados.

    Args:
        loja_url (str): A URL base da loja a ser acessada (ex: "https://www.minhaloja.com").
        nicho_busca (str): O nicho ou categoria de produtos a ser pesquisado (ex: "eletrônicos").
        quantidade_produtos (int): O número máximo de produtos a serem coletados.

    Returns:
        dict: Um dicionário contendo os dados dos produtos coletados no formato de saída.
    """

    logger.debug(f"[scrape_store_products] parâmetros recebidos: {locals()}")

    crew_product_scraper = Crew(
        agents=[
            ecommerce_structure_specialist,
            # store_navigator_agent,
            # product_structure_analyst,
            # product_listing_agent,
            # product_detail_extractor_agent,
            # product_data_curator_agent,
            # affiliate_output_formatter_agent,
            # product_database_inserter_agent
        ],
        tasks=[
            identify_ecomerce_structure_task,
            # navigate_and_search_store_task,
            # analyze_scraped_html_task, 
            # identify_product_urls_task,
            # extract_individual_product_details_task,
            # clean_and_format_product_data_task,
            # build_pydantic_objects_task,
            # insert_scraped_products_task 
        ],
        process=Process.sequential,  # O processamento é sequencial para garantir o fluxo de dados
        verbose=True,  # Exibe o progresso da crew
        max_rpm=250,
    
    )

    # O método kickoff recebe um dicionário 'inputs'
    # As chaves aqui devem corresponder aos placeholders que você usaria na descriçao das tarefas
    resultado_raspagem = crew_product_scraper.kickoff(
        inputs={
            'loja_url': loja_url,
            'nicho_busca': nicho_busca,
            'quantidade_produtos': quantidade_produtos
        }
    )

    return {
        "produtos_para_afiliados": resultado_raspagem
    }
