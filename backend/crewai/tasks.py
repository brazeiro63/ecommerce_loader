# backend/crewai/tasks.py
from crewai import Task
from crewai_tools import ScrapeWebsiteTool, SeleniumScrapingTool, SerperDevTool

from backend.crewai.agents import (affiliate_output_formatter_agent,
                                   database_inserter, output_formatter,
                                   product_data_curator_agent,
                                   product_database_inserter_agent,
                                   product_detail_extractor_agent,
                                   product_listing_agent,
                                   product_structure_analyst,
                                   public_api_searcher, store_curator,
                                   store_navigator_agent, store_researcher)
from backend.crewai.my_llm import MyLLM
from backend.crewai.tools import (insert_affiliate_stores_tool,
                                  insert_product_list_tool, read_website_content)

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
    tools=[serper_tool, read_website_content] 
)

analyze_scraped_html_task = Task(
    description=(
        "Você receberá o conteúdo HTML completo de uma página de e-commerce. "
        "Seu trabalho é analisar a estrutura do HTML e identificar padrões que representem blocos de produtos. "
        "Isso inclui elementos como nome do produto, preço, imagem, links e avaliações.\n\n"
        "Identifique os seletores ou estruturas comuns (por exemplo: divs com a mesma classe ou padrão) "
        "e produza um relatório com:\n"
        "- Número estimado de blocos de produtos\n"
        "- Campos detectados (nome, preço, imagem, etc.)\n"
        "- Classe/CSS selector de cada campo\n"
        "- Observações sobre a estrutura\n\n"
        "Seu relatório deve ser preciso, legível e com sugestões para extração automática posterior."
    ),
    expected_output=(
        "Um relatório em texto estruturado com as informações listadas acima sobre a estrutura de produtos na página HTML."
    ),
    agent=product_structure_analyst
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
    tools=[read_website_content]
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
    tools=[read_website_content, scraper_tool] # Agente precisa do Selenium para acessar e extrair detalhes de cada página de produto
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


build_pydantic_objects_task = Task(
    description=
    """
        Transformar os dados dos produtos em objetos do tipo ProductCreate,
        utilizando o schema Pydantic definido a seguir.
            class ProductCreate(BaseModel):
                external_id: str
                platform: str
                title: str
                description: str
                price: float
                sale_price: Optional[float] = None
                image_url: Optional[str] = None
                product_url: str
                category: str
                brand: Optional[str] = None
                available: bool = True
    """,
    expected_output="""
        Lista de objetos ProductCreate com todos os campos corretos para persistência.
    """,
    agent=affiliate_output_formatter_agent,
    context=[clean_and_format_product_data_task],
    llm=my_llm.GTP4o_mini
)

insert_scraped_products_task = Task(
    description="""
        Utilizar a ferramenta InsertProductListTool para persistir os produtos no banco.
    """,
    expected_output="""
        Confirmação de inserção e lista dos IDs ou mensagem de sucesso.
    """,
    agent=product_database_inserter_agent,
    tools=[insert_product_list_tool],
    input_tasks=[build_pydantic_objects_task],
    context=[build_pydantic_objects_task],
    llm=my_llm.GTP4o_mini
)


