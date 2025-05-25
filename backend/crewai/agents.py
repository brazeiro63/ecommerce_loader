# backend/crewai/agents.py
from crewai import Agent

from backend.crewai.tools import insert_affiliate_stores_tool

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
