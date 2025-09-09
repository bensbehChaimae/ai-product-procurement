from crewai import Agent, Task
from crewai.tools import tool
from pydantic import BaseModel, Field
from typing import List
from tavily import TavilyClient

class SingleSearchResult(BaseModel):
    title: str
    url: str = Field(..., title="the page url")
    content: str
    score: float
    search_query: str

class AllSearchResults(BaseModel):
    results: List[SingleSearchResult]

class AgentB:
    """Agent responsible for performing web searches using Tavily"""
    
    def __init__(self, basic_llm, search_client: TavilyClient):
        self.basic_llm = basic_llm
        self.search_client = search_client
        
    @tool
    def search_engine_tool(self, query: str) -> dict:
        """Useful for search-based queries. Use this to find current information about any query related pages using a search engine"""
        return self.search_client.search(query)
    
    def create_agent(self):
        return Agent(
            role="Search Engine Agent",
            goal="To search for products based on the suggested search query",
            backstory="The agent is designed to help in looking for products by searching for products based on the suggested search queries.",
            llm=self.basic_llm,
            verbose=True,
            tools=[self.search_engine_tool]
        )
    
    def create_task(self, product_name: str, websites_list: List[str], country_name: str):
        return Task(
            description="\n".join([
                f"RankX is looking to buy {product_name} at the best prices (value for a price strategy).",
                f"The company target any of these websites to buy from: {websites_list}.",
                f"The company wants to reach all available products on the internet to be compared later in another stage.",
                f"The stores must sell the product in {country_name}.",
                "Collect the best search results from the search results.",
            ]),
            expected_output="A JSON object containing a list of search results.",
            output_json=AllSearchResults,
            output_file="step_2_search_results.json",
            agent=self.create_agent()
        )