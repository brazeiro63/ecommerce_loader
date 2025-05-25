# backend/crewai/crew_products.py
from crewai import Crew, Process
from backend.crewai.agents import *
from backend.crewai.tasks import *

def discover_products(tema):

    crew1 = Crew(
        agents=[store_researcher],
        tasks=[research_affiliate_stores],
        process=Process.sequential
    )

    crew2 = Crew(
        agents=[store_curator],
        tasks=[curate_top_affiliate_stores],
        process=Process.sequential
    )

    resultado1 = crew1.kickoff(inputs={'tema': tema})
    resultado2 = crew2.kickoff(inputs={'tema': tema})

    return {
        "pesquisa": resultado1,
        "artigo": resultado2
    }
