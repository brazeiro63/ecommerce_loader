# backend/crewai/tasks.py
from crewai import Task

from backend.crewai.agents import * 
from backend.crewai.my_llm import MyLLM
from backend.crewai.tools import insert_affiliate_stores_tool

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
        A list of affiliate stores including name, platform, and commission 
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
        name, platform and rationale for each selection.
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
        - api_credentials: Um dicionário com as credenciais da API da loja, 
            por exemplo {'api_key': 'abc', 'secret': 'xyz'}
    """,
    expected_output=
    """
        JSON válido que represente uma lista de AffiliateStoreCreate com todos 
        os campos preenchidos
    """,
    llm=my_llm.GTP4o_mini,
    agent=output_formatter
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
)


