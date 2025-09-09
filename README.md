# AI-Powered Multi-Agent System for Automated Product Procurement

Companies often face significant challenges in procurement: teams spend countless hours manually searching for suppliers, gathering product information, and compiling reports for decision-making. This process is repetitive, time-consuming, and prone to human error, especially when dealing with large-scale sourcing needs.

This project addresses this challenge by simulating the operations of a procurement department using AI agents. Each agent is responsible for a specific task—such as generating search queries, crawling the web for suppliers, extracting detailed product information, and compiling results into a structured format.


## Table of Contents  

- [Project Description](#-project-description)  
- [Features](#features)  
- [Tools & Technologies](#-tools--technologies)  
- [Agents Overview](#agents-overview-)  
- [Workflow](#workflow)  
- [Installation](#installation)  
- [Usage](#usage)  
  - [Option 1: FastAPI Interface](#option-1-fastapi-interface)  
  - [Option 2: Streamlit Interface](#option-2-streamlit-interface)  
- [API Endpoints](#api-endpoints)  
- [File Structure](#file-structure)  
- [Output Files](#output-files)  
- [Customization](#customization)  
  - [Adding New Agents](#adding-new-agents)  
  - [Modifying Search Behavior](#modifying-search-behavior)  
  - [Customizing Reports](#customizing-reports)  
- [Troubleshooting](#troubleshooting)  
  - [Common Issues](#common-issues)  
  - [Debugging](#debugging)  
- [Contributing](#contributing)  
- [License](#license)  


## Features

- **Multi-Agent Architecture**: Uses CrewAI to orchestrate specialized agents for different tasks
- **Web Search**: Automated search query generation and web searching using Tavily
- **Web Scraping**: Intelligent product data extraction using ScrapGraph AI
- **Report Generation**: Professional HTML procurement reports with Bootstrap styling
- **Dual Interface**: Both FastAPI REST API and Streamlit web interface



## Tools & Technologies  

- **[CrewAI](https://github.com/joaomdmoura/crewAI)** → Multi-agent orchestration framework  

- **[Travily](https://www.tavily.com/)** → used to perform web searches and retrieve structured results from Google.

- **[AgentOps](https://www.agentops.ai/)** → Monitoring, observability, and performance tracking for AI agents 

- **[Scrap GraphAI](https://github.com/your-repo/scrap-graphai)** → Web scraping and graph-based data extraction tool  



## Agents overview :

The system consists of 4 specialized agents:

![agents](/src/assets/ai_agent.png)

### Agent A : Keyword Strategist

* **Role:** Research Initiator
* **Task:** Generate a list of suggested queries (keywords) to feed into the search engine.
* **Tools:** Native keyword extraction skills.
* **Output:** Keywords list.


### Agent B : Market Explorer

* **Role:** Online Searcher
* **Task:** Perform web searches for products using the keywords.
* **Tools:** https://tavily.com a free alternative for Google Search API (paid)
* **Output:** List of relevant web results.


### Agent C : Data Extractor

* **Role:** Information Miner
* **Task:** Parse and extract product details (pricing, specs, supplier info) from web pages.
* **Tools:** https://scrapegraphai.com 
* **Output:** Structured product details.


### Agent D : Report Generator 

* **Role:** Procurement Analyst
* **Task:** Transform structured product details into a professional, human-readable procurement report.
* **Tools:** HTML/PDF report generator.
* **Output:** Visual, ready-to-share procurement report.


## Workflow

1. **Agent A:** Extracts relevant keywords.
2. **Agent B:** Searches for products on the web.
3. **Agent C:** Extracts structured details from product pages.
4. **Agent D:** Compiles data into a professional procurement report.


## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ai-product-procurement
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

Required API keys:
- `OPENAI_API_KEY`: OpenAI API key for LLM
- `AGENTOPS_API_KEY`: AgentOps API key for monitoring (optional)
- `TAVILY_API_KEY`: Tavily API key for web search
- `SCRAPEGRAPH_API_KEY`: ScrapGraph AI API key for web scraping

## Usage

### Option 1: FastAPI Interface

1. **Start the FastAPI server**:
```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. **Open your browser** and go to `http://localhost:8000`

3. **Fill in the research parameters**:
   - Product name (e.g., "Office air conditioners")
   - Target websites (one per line)
   - Country and language settings
   - Advanced parameters (keywords count, score threshold, etc.)

4. **Start research** and monitor progress in real-time

5. **Download results** including HTML reports and JSON data files

### Option 2: Streamlit Interface

1. **Start the Streamlit app**:
```bash
streamlit run streamlit_app.py
```

2. **Configure API keys** in the sidebar

3. **Enter research parameters** and start the research

4. **View results** and download files directly from the interface

## API Endpoints

- `POST /api/research`: Start a new research job
- `GET /api/job/{job_id}/status`: Check job status
- `GET /api/job/{job_id}/download/{filename}`: Download output files
- `GET /api/job/{job_id}/files`: List all output files
- `GET /api/jobs`: List all jobs

## File Structure

```
├── agentA.py              # Search query generation agent
├── agentB.py              # Web search agent
├── agentC.py              # Web scraping agent
├── agentD.py              # Report generation agent
├── crew_manager.py        # Main crew orchestrator
├── main.py                # FastAPI application
├── streamlit_app.py       # Streamlit interface
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── ai_agent_output/      # Output directory (created automatically)
```

## Output Files

The system generates several output files:

1. `step_1_suggested_search_queries.json`: Generated search queries
2. `step_2_search_results.json`: Web search results
3. `step_3_search_results.json`: Extracted product details
4. `step_4_procurement_report.html`: Final HTML report

## Customization

### Adding New Agents

1. Create a new agent file (e.g., `agentE.py`)
2. Follow the existing pattern with agent creation and task definition
3. Add the agent to `crew_manager.py`

### Modifying Search Behavior

- Edit `agentA.py` to change search query generation logic
- Modify `agentB.py` to adjust web search parameters

### Customizing Reports

- Edit `agentD.py` to modify the HTML report structure and styling
- Add custom CSS or JavaScript to enhance the report appearance

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set in `.env` file
2. **Import Errors**: Check that all dependencies are installed correctly
3. **Permission Errors**: Ensure the output directory is writable
4. **Rate Limiting**: Some APIs have rate limits; consider adding delays if needed

### Debugging

- Set `verbose=True` in agent configurations for detailed logging
- Check the console output for detailed error messages
- Verify API key validity and account quotas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

