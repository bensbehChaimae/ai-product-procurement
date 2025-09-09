from crewai import Agent, Task
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

class AgentD:
    """Agent responsible for generating the final procurement report"""
    
    def __init__(self, basic_llm, company_context: StringKnowledgeSource):
        self.basic_llm = basic_llm
        self.company_context = company_context
        
    def create_agent(self):
        return Agent(
            role="Procurement Report Author Agent",
            goal="To generate a professional HTML page for the procurement report",
            backstory="The agent is designed to assist in generating a professional HTML page for the procurement report after looking into a list of products.",
            llm=self.basic_llm,
            verbose=True,
        )
    
    def create_task(self):
        return Task(
            description="\n".join([
                "The task is to generate a professional HTML page for the procurement report.",
                "You have to use Bootstrap CSS framework for a better UI.",
                "Use the provided context about the company to make a specialized report.",
                "The report will include the search results and prices of products from different websites.",
                "The report should be structured with the following sections:",
                "1. Executive Summary: A brief overview of the procurement process and key findings.",
                "2. Introduction: An introduction to the procurement objective and scope of the report.",
                "3. Methodology: A description of the methods used to gather and compare prices.",
                "4. Findings: Detailed comparison of prices from different websites, including tables and charts.",
                "5. Analysis: An analysis of the findings, highlighting any significant trends or observations.",
                "6. Recommendations: Suggestions for procurement based on the analysis.",
                "7. Conclusion: A summary of the report and final thoughts.",
                "8. Appendices: Any additional information, such as raw data or supplementary materials.",
            ]),
            expected_output="A professional HTML page for the procurement report.",
            output_file="step_4_procurement_report.html",
            agent=self.create_agent()
        )