
from crewai import Agent, Task
from crewai.tools import tool
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from pydantic import BaseModel, Field
from typing import List

class SuggestedSearchQueries(BaseModel):
    queries: List[str] = Field(..., title="Suggested search queries to be passed to the search engine", 
                              min_items=1, max_items=20)

class AgentA:
    """Agent responsible for generating search queries based on product and context"""
    
    def __init__(self, basic_llm, company_context: StringKnowledgeSource):
        self.basic_llm = basic_llm
        self.company_context = company_context
        
    def create_agent(self):
        return Agent(
            role="Search Queries Recommendation Agent",
            goal="\n".join([
                "To provide a list of suggested search queries to be passed to the search engine.",
                "The queries must be varied and looking for specific items."
            ]),
            backstory="The agent is designed to help in looking for products by providing a list of suggested search queries to be passed to the search engine based on the context provided.",
            llm=self.basic_llm,
            verbose=True,
        )
    
    def create_task(self, product_name: str, websites_list: List[str], country_name: str, 
                   language: str, no_keywords: int):
        return Task(
            description="\n".join([
                f"RankX is looking to buy {product_name} at the best prices (value for a price strategy).",
                f"The company target any of these websites to buy from: {websites_list}.",
                f"The company wants to reach all available products on the internet to be compared later in another stage.",
                f"The stores must sell the product in {country_name}.",
                f"Generate at maximum {no_keywords} queries.",
                f"The search keywords must be in {language} language.",
                "Search keywords must contains specific brands, types or technologies. Avoid general keywords.",
                "The search query must reach an ecommerce webpage for the product, and not a blog or listing page."
            ]),
            expected_output="A JSON object containing a list of suggested search queries.",
            output_json=SuggestedSearchQueries,
            output_file="step_1_suggested_search_queries.json",
            agent=self.create_agent()
        )