import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # API Keys
    openai_api_key: str
    agentops_api_key: Optional[str] = None
    tavily_api_key: str
    scrapegraph_api_key: str
    
    # Application Settings
    app_env: str = "development"
    log_level: str = "INFO"
    max_concurrent_jobs: int = 2
    
    # Directories
    output_dir: str = "./ai_agent_output"
    
    # LLM Settings
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.0
    
    # Default Company Context
    company_name: str = "RankX"
    company_description: str = "RankX is a company that provides AI solutions to help websites refine their search and recommendation systems."
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()

def validate_api_keys(settings: Settings) -> dict:
    """Validate that required API keys are present"""
    errors = []
    
    if not settings.openai_api_key:
        errors.append("OPENAI_API_KEY is required")
    
    if not settings.tavily_api_key:
        errors.append("TAVILY_API_KEY is required")
    
    if not settings.scrapegraph_api_key:
        errors.append("SCRAPEGRAPH_API_KEY is required")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def ensure_output_directory(settings: Settings) -> None:
    """Ensure output directory exists"""
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)