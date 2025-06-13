# backend/crewai/agents.py
from crewai import Agent
from crewai_tools import (
    ScrapeWebsiteTool, 
    # SeleniumScrapingTool, 
    SerperDevTool
    )

from backend.crewai.tools.tools import (
    insert_affiliate_stores_tool,
    insert_product_list_tool,
    read_website_content
    )
from backend.crewai.tools.autodetect_product_selectors_tool  import autodetect_product_selectors
from backend.crewai.tools.count_html_structures_tool import count_repeated_html_structures 

serper_tool = SerperDevTool(
    country="br",
    locale="pt-BR",
    n_results=20,
)
# selenium_tool = SeleniumScrapingTool()
scraper_tool = ScrapeWebsiteTool()

store_researcher = Agent(
    role='Affiliate Program Store Researcher',
    goal='Discover online stores with affiliate programs offering products '
    'in the {nicho} niche during the {periodo} period in {pais}.',
    backstory='You are an experienced researcher specialized in affiliate ' \
    'marketing. You use search engines, affiliate directories, and social ' \
    'signals to find high-potential stores within specified niches and ' \
    'regions.',
    verbose=True,
    memory=False
)

store_curator = Agent(
    role='Affiliate Store Curator',
    goal=
    'Select the top 5 affiliate stores from the list based on commission rate '
    'and reputation.',
    backstory=
    'You are an expert in affiliate program evaluation, known for your ' \
    'critical eye. You assess trustworthiness, commission percentages, and '
    'market feedback to select only the most profitable and reliable stores.',
    verbose=True,
    memory=False
)

public_api_searcher = Agent(
    role='Public API Searcher',
    goal='discover of existing public api service for product search',
    backstory=
    'You are an able website researcher specilized in finding public api' \
    'givem a existing store.',
    tools=[serper_tool],
    verbose=True,
    memory=False
)

output_formatter = Agent(
    role='Formatter',
    goal='format data as asked',
    backstory=
    'You are a data format expert that identifies all aspect needed to ' \
    'create well formatted documents in any file type formats.',
    verbose=True,
    memory=False
)

database_inserter = Agent(
    role='Data Inserter',
    goal=
    'Ensure that approved affiliate stores and their products are correctly ' \
    'saved to the database.',
    backstory=
    'You are responsible for validating and persisting all structured data ' \
    'into the systems backend.  You work with precision, especially when ' \
    'dealing with store credentials and product attributes',
    tools=[insert_affiliate_stores_tool],
    verbose=True,
    memory=False
)

product_trend_analyst = Agent(
    role='Product Trend Analyst',
    goal=
    'Identify which products within the {nicho} niche were most searched ' \
    'for during the {periodo} period.',
    backstory=
    'You specialize in analyzing search trends and customer behavior. You ' \
    'use tools like Google Trends, search APIs, and market data to identify ' \
    'trending products in specific niches.',
    verbose=True,
    memory=False
)

product_scraper = Agent(
    role='E-commerce Product Scraper',
    goal=
    'Collect up to 100 products from each affiliate store related to the ' \
    'most searched product names within the {nicho} niche.',
    backstory=
    'You are a web crawler specialized in extracting structured data from ' \
    'online stores. You follow guidelines to ensure data consistency and ' \
    'relevance for affiliate business strategies.',
    verbose=True,
    memory=False
)

product_structure_analyst = Agent(
    role='Especialista em Estrutura de E-commerce',
    goal='Detectar padrões e estruturas de produto em páginas HTML de e-commerce',
    verbose=True,
    memory=True,
    backstory=(
    "Você é um especialista em entender como sites de e-commerce organizam visualmente "
    "seus produtos. Com experiência em HTML e análise estrutural, sua missao é encontrar "
    "blocos de dados repetitivos que representem produtos e identificar campos como nome, "
    "preço e imagens para futura extraçao automatizada."
    ),
    tools=[count_repeated_html_structures]
)

ecommerce_structure_specialist = Agent(
    role="Scraper Inteligente",
    goal="Detectar automaticamente seletores de produto em e-commerce",
    backstory="Você é um especialista em formatação de frontend de ecommerce",
    tools=[autodetect_product_selectors]
)

store_navigator_agent = Agent(
    role='Navegador de Websites e Buscador Inicial',
    goal=
    'Acessar o site da loja fornecida e iniciar a busca pelo nicho especificado, '
    'navegando pela interface do site para encontrar a página de resultados da busca.',
    backstory=
    'Você é um especialista em automaçao de navegaçao web e interaçao com formulários de busca. '
    'Sua expertise inclui superar desafios comuns como pop-ups, CAPTCHAs, e diferentes layouts de site '
    'para garantir o acesso eficiente aos resultados de busca. Você é o ponto de entrada para a coleta de dados.',
    tools=[scraper_tool, read_website_content],
    verbose=True,
    memory=False
)

product_listing_agent = Agent(
    role='Extrator de Listagem de Produtos',
    goal=
    'Navegar pelas páginas de resultados de busca, identificar e coletar os URLs de produtos '
    'relevantes até a quantidade definida, gerenciando a paginaçao se necessário.',
    backstory=
    'Você é um extrator de dados altamente proficiente, especializado em identificar e coletar links '
    'de listagens de produtos em páginas de resultados de busca. Sua habilidade em lidar com diferentes '
    'estruturas HTML e mecanismos de paginaçao garante que todos os URLs necessários sejam capturados com precisao.',
    tools=[scraper_tool, read_website_content],
    verbose=True,
    memory=False
)

product_detail_extractor_agent = Agent(
    role='Detalhista de Informações de Produto',
    goal=
    'Acessar cada URL de produto coletado e extrair todas as informações detalhadas solicitadas: '
    'nome, descriçao, URLs de imagem, preço normal, preço promocional, validade da oferta, '
    'e outras informações relevantes para afiliados.',
    backstory=
    'Sua especialidade é o deep scraping, capaz de mergulhar em páginas individuais de produtos para '
    'extrair dados estruturados e semi-estruturados. Você é mestre em adaptar-se a diferentes layouts de '
    'lojas online, identificando e recuperando os elementos específicos de cada produto com alta precisao.',
    tools=[scraper_tool, read_website_content],
    verbose=True,
    memory=False
)

product_data_curator_agent = Agent(
    role='Curador e Normalizador de Dados de Produto',
    goal=
    'Limpar, validar, padronizar e enriquecer os dados brutos extraídos dos produtos, '
    'garantindo consistência e qualidade para uso posterior na loja de afiliados.',
    backstory=
    'Você é um engenheiro de dados metódico e preciso. Sua funçao é transformar dados brutos '
    'em informações limpas e padronizadas. Você aplica regras de validaçao, remove inconsistências, '
    'converte tipos de dados e garante que cada campo esteja no formato ideal para consumo por sistemas de afiliados.',
    verbose=True,
    memory=False
)

affiliate_output_formatter_agent = Agent(
    role='Formatador Final de Dados para Afiliados',
    goal=
    'Organizar os dados curados dos produtos em um formato de saída final, '
    'otimizado para integraçao com plataformas de afiliados, como uma lista de objetos JSON/Python.',
    backstory=
    'Você é um especialista em estruturaçao de dados para integraçao de sistemas. '
    'Sua expertise reside em pegar informações processadas e apresentá-las em um formato que seja '
    'facilmente consumível por outras aplicações, garantindo que a saída seja precisa, completa e '
    'pronta para uso em uma loja de afiliados.',
    verbose=True,
    memory=False
)

product_database_inserter_agent = Agent(
    role='Database Inserter for Products',
    goal='Persistir os produtos extraídos no banco de dados da loja de afiliados',
    backstory=(
        'Você é responsável por receber uma lista de produtos limpos e formatados, '
        'validar a estrutura de cada item e inserir no banco de forma eficiente e segura.'
    ),
    tools=[insert_product_list_tool],
    verbose=True,
    memory=False
)