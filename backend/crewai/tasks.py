# backend/crewai/tasks.py
from crewai import Task
from crewai_tools import SerperDevTool, SeleniumScrapingTool, ScrapeWebsiteTool

from backend.crewai.my_llm import MyLLM
from backend.crewai.tools import insert_affiliate_stores_tool
from backend.crewai.agents import (
    store_researcher,
    store_curator,
    output_formatter,
    public_api_searcher,
    database_inserter
) 
from backend.crewai.agents import (
    store_navigator_agent,
    product_listing_agent,
    product_detail_extractor_agent,
    product_data_curator_agent,
    affiliate_output_formatter_agent
)

scraper_tool = ScrapeWebsiteTool()
selenium_tool = SeleniumScrapingTool()
serper_tool = SerperDevTool()
my_llm = MyLLM()

research_affiliate_stores = Task(
    description=
    """
       Research and compile a list of online stores that offer affiliate 
       programs with products in the {nicho} niche, active during the 
       {periodo} period within the country {pais}. Use search engines, 
       affiliate networks, and marketplaces to identify opportunities. 
    """,
    expected_output=
    """
        A list of affiliate stores including name, url, platform, and commission 
        program details.
    """, 
    llm=my_llm.GTP4o_mini,
    agent=store_researcher
)

curate_top_affiliate_stores = Task(
    description=
    """
       Evaluate the list of discovered affiliate stores based on their 
       commission rates and market reputation. Select the top 5 most 
       promising stores for partnership. 
    """,
    expected_output=
    """
        A refined list with the 5 best affiliate stores including 
        name, url, platform and rationale for each selection.
    """,
    llm=my_llm.GTP4o_mini,
    agent=store_curator
)

format_output = Task(
    description=
    """
        Crie uma lista de objetos do tipo AffiliateStoreCreate com os 
        seguintes campos: 
        - name: Nome da loja
        - platform: Plataforma usada (ex: Shopify, WooCommerce)
        - active: Booleano indicando se a loja está ativa
        - url: URL da loja
        - api_credentials: Um dicionário com as credenciais da API da loja, 
            por exemplo 
            {
                'has_public_api': 'True, 
                'url_public_api': 'www.public_api.com.br', 
                api_key': 'abc', 
                'secret': 'xyz'
            }
    """,
    expected_output=
    """
        JSON válido que represente uma lista de AffiliateStoreCreate com todos 
        os campos preenchidos
    """,
    llm=my_llm.GTP4o_mini,
    agent=output_formatter
)

search_public_api = Task(
    description=
    """
        Busque, para as lojas selecionadas, se existe disponível uma API pública
        para consulta de produtos. Se existir, colete a url do endpoint de
        consulta de produtos.
    """,
    expected_output=
    """
        Leia o JSON de entrada. Para cada item, preencha as propriedades 
        has_public_api e public_api_url do elemento api_credentials.
        Complemente o JSON, acrescentando no dicionário em api_credencials,
        has_public_api: boolean, url_public_api: str || none.
    """ ,
    llm=my_llm.GTP4o_mini,
    tools=[serper_tool],
    agent=public_api_searcher,
    context=[format_output]
)

insert_curated_stores = Task(
    description=
    """
       Utilize o InsertAffiliateStoresTool para inserir os dados gerados anteriormente. 
       As lojas estão no formato AffiliateStoreCreate. 
       Use a função InsertAffiliateStoresTool passando a lista como argumento.
    """,
    expected_output=
    """
        Confirmation with the IDs of each store successfully inserted.
    """, 
    agent=database_inserter,
    tools=[insert_affiliate_stores_tool],
    input_tasks=[format_output],
    llm=my_llm.GTP4o_mini,
    context=[format_output,search_public_api]
)

navigate_and_search_store_task = Task(
    description=
    """
       Acessar a loja online '{loja_url}' e navegar até a funcionalidade de busca.
       Realizar uma busca pelo nicho de produtos '{nicho_busca}' e garantir que a página
       de resultados da busca seja carregada com sucesso.
       A saída deve conter o conteúdo HTML da página de resultados da busca ou um identificador único para essa página.
    """,
    expected_output=
    """
        O conteúdo HTML completo da página de resultados da busca para o nicho especificado,
        pronto para a extração de URLs de produtos.
    """,
    llm=my_llm.GTP4o_mini,
    agent=store_navigator_agent,
    tools=[serper_tool, selenium_tool] 
)

identify_product_urls_task = Task(
    description=
    """
       A partir do conteúdo HTML da página de resultados da busca, identificar e extrair os URLs
       individuais de até '{quantidade_produtos}' produtos que pertencem ao nicho '{nicho_busca}'.
       Priorizar produtos mais relevantes ou em destaque, se houver.
    """,
    expected_output=
    """
        Uma lista Python contendo os URLs completos (strings) de cada um dos produtos identificados,
        limitada à 'quantidade_produtos' especificada.
    """,
    llm=my_llm.GTP4o_mini,
    agent=product_listing_agent,
    tools=[selenium_tool]
)

extract_individual_product_details_task = Task(
    description=
    """
       Para cada URL de produto fornecido, acessar a página individual do produto e extrair
       as seguintes informações: nome do produto, descrição completa, URL(s) da imagem principal e secundárias,
       preço normal, preço promocional (se houver), validade da oferta (se aplicável),
       e quaisquer outras informações relevantes para a criação de uma listagem de afiliado (ex: SKU, marca, categorias).
    """,
    expected_output=
    """
        Uma lista de dicionários Python, onde cada dicionário representa um produto
        e contém todos os detalhes brutos extraídos (nome, descrição, preços, imagens, etc.).
        Exemplo: [{'nome': 'Produto A', 'preco_normal': 'R$ 100,00', ...}, ...]
    """,
    llm=my_llm.GTP4o_mini,
    agent=product_detail_extractor_agent,
    tools=[selenium_tool, scraper_tool] # Agente precisa do Selenium para acessar e extrair detalhes de cada página de produto
)

clean_and_format_product_data_task = Task(
    description=
    """
       Pegar a lista de dicionários de produtos com informações brutas e realizar a limpeza,
       validação e padronização dos dados. Isso inclui converter valores de preço para formato numérico (float),
       remover caracteres indesejados, garantir que todos os campos estejam presentes e no tipo correto,
       e formatar descrições e URLs de imagens para consistência.
    """,
    expected_output=
    """
        Uma lista de dicionários Python onde cada dicionário de produto tem seus dados
        limpos, validados e padronizados. Exemplo:
        [{'nome': 'Produto A', 'preco_normal': 100.00, 'preco_promocional': None,
          'imagens': ['url_img1', 'url_img2'], 'validade_oferta': 'YYYY-MM-DD', ...}, ...]
    """,
    llm=my_llm.GTP4o_mini,
    agent=product_data_curator_agent,
    tools=[] # Este agente não precisa de ferramentas externas para esta tarefa
)

generate_affiliate_product_list_task = Task(
    description=
    """
       Finalizar a formatação dos dados dos produtos já limpos e padronizados,
       organizando-os em uma estrutura de saída ideal para ser utilizada diretamente
       na criação de uma loja de afiliados.
    """,
    expected_output=
    """
        Um objeto JSON ou uma estrutura de dados Python (lista de dicionários) final,
        representando a coleção completa de produtos com todas as informações
        necessárias para um catálogo de afiliados, pronto para ingestão em um banco de dados
        ou exibição em uma plataforma de e-commerce.
    """,
    llm=my_llm.GTP4o_mini,
    agent=affiliate_output_formatter_agent,
    tools=[] # Este agente não precisa de ferramentas externas para esta tarefa
)