from crewai import Crew, Process, LLM
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from tavily import TavilyClient
from scrapegraphai import Client
import os
from typing import List, Dict, Any
import json

from agent_A import AgentA
from agent_B import AgentB
from agent_C import AgentC
from agent_D import AgentD

class CrewManager:
    """Main class to orchestrate all agents and manage the crew execution"""
    
    def __init__(self):
        self.setup_environment()
        self.setup_clients()
        self.setup_knowledge_base()
        self.setup_agents()
        
    def setup_environment(self):
        """Setup environment variables and basic configurations"""
        # These should be set as environment variables or passed as parameters
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.agentops_api_key = os.getenv("AGENTOPS_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.scrapegraph_api_key = os.getenv("SCRAPEGRAPH_API_KEY")
        
        # Setup basic LLM
        self.basic_llm = LLM(model="gpt-4o", temperature=0)
        
        # Setup output directory
        self.output_dir = "./ai_agent_output"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def setup_clients(self):
        """Initialize external service clients"""
        self.search_client = TavilyClient(api_key=self.tavily_api_key)
        self.scrape_client = Client(api_key=self.scrapegraph_api_key)
        
    def setup_knowledge_base(self):
        """Setup company knowledge base"""
        about_company = "RankX is a company that provides AI solutions to help websites refine their search and recommendation systems."
        self.company_context = StringKnowledgeSource(content=about_company)
        
    def setup_agents(self):
        """Initialize all agents"""
        self.agent_a = AgentA(self.basic_llm, self.company_context)
        self.agent_b = AgentB(self.basic_llm, self.search_client)
        self.agent_c = AgentC(self.basic_llm, self.scrape_client)
        self.agent_d = AgentD(self.basic_llm, self.company_context)
        
    def create_crew(self, inputs: Dict[str, Any]):
        """Create and configure the crew with all agents and tasks"""
        
        # Extract inputs
        product_name = inputs["product_name"]
        websites_list = inputs["websites_list"]
        country_name = inputs["country_name"]
        no_keywords = inputs["no_keywords"]
        language = inputs["language"]
        score_th = inputs["score_th"]
        top_recommendations_no = inputs["top_recommendations_no"]
        
        # Create tasks for each agent
        search_queries_task = self.agent_a.create_task(
            product_name, websites_list, country_name, language, no_keywords
        )
        
        search_engine_task = self.agent_b.create_task(
            product_name, websites_list, country_name
        )
        
        scraping_task = self.agent_c.create_task(top_recommendations_no)
        
        procurement_report_task = self.agent_d.create_task()
        
        # Create crew
        crew = Crew(
            agents=[
                self.agent_a.create_agent(),
                self.agent_b.create_agent(),
                self.agent_c.create_agent(),
                self.agent_d.create_agent(),
            ],
            tasks=[
                search_queries_task,
                search_engine_task,
                scraping_task,
                procurement_report_task,
            ],
            process=Process.sequential,
            knowledge_sources=[self.company_context]
        )
        
        return crew
    
    def execute_crew(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the crew with given inputs"""
        try:
            crew = self.create_crew(inputs)
            results = crew.kickoff(inputs=inputs)
            
            return {
                "success": True,
                "results": results,
                "output_directory": self.output_dir
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output_directory": self.output_dir
            }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        required_fields = [
            "product_name", "websites_list", "country_name", 
            "no_keywords", "language", "score_th", "top_recommendations_no"
        ]
        
        errors = []
        
        for field in required_fields:
            if field not in inputs:
                errors.append(f"Missing required field: {field}")
        
        if "websites_list" in inputs and not isinstance(inputs["websites_list"], list):
            errors.append("websites_list must be a list of website URLs")
            
        if "no_keywords" in inputs and not isinstance(inputs["no_keywords"], int):
            errors.append("no_keywords must be an integer")
            
        if "score_th" in inputs and not isinstance(inputs["score_th"], (int, float)):
            errors.append("score_th must be a number")
            
        if "top_recommendations_no" in inputs and not isinstance(inputs["top_recommendations_no"], int):
            errors.append("top_recommendations_no must be an integer")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }