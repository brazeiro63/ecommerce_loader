# backend/crewai/crew_stores.py
from crewai import Crew, Process

from backend.crewai.agents import *
from backend.crewai.tasks import *


def discover_stores(pais, nicho, periodo):

    crew1 = Crew(
        agents=[
            store_researcher, 
            store_curator,
            output_formatter, 
            public_api_searcher,
            database_inserter
        ],
        tasks=[
            research_affiliate_stores, 
            curate_top_affiliate_stores,
            format_output,
            search_public_api,
            insert_curated_stores
        ],
        process=Process.sequential
    )


    resultado1 = crew1.kickoff(
        inputs={'pais': pais, 'nicho': nicho, 'periodo': periodo}
    )

    return {
        "pesquisa": resultado1
    }
