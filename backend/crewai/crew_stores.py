# backend/crewai/crew_stores.py
from crewai import Crew, Process
from backend.crewai.agents import *
from backend.crewai.tasks import *

def executar_stores(pais, nicho, periodo):

    crew1 = Crew(
        agents=[
            store_researcher, 
            store_curator,
            output_formatter, 
            database_inserter
        ],
        tasks=[
            research_affiliate_stores, 
            curate_top_affiliate_stores,
            format_output, 
            insert_curated_stores
        ],
        process=Process.sequential
    )


    resultado1 = crew1.kickoff(
        inputs={'pais': pais, 'nicho': nicho, 'periodo': periodo}
    )
    # resultado2 = crew2.kickoff(inputs={'tema': tema})

    return {
        "pesquisa": resultado1
        # "artigo": resultado2
    }
