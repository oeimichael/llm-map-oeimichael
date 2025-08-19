import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings:
    # Google Maps Configuration
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    GOOGLE_MAPS_JS_API_KEY: str = os.getenv("GOOGLE_MAPS_JS_API_KEY", "")
    
    # LLM Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3:1b")
    
    # Security Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080,http://127.0.0.1:5500").split(",")
    API_KEY_HEADER: str = "X-API-Key"
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # Application Configuration
    MAX_LOCATIONS_RETURNED: int = int(os.getenv("MAX_LOCATIONS_RETURNED", "5"))
    MAPS_SEARCH_RADIUS: int = int(os.getenv("MAPS_SEARCH_RADIUS", "50000"))  # 50km
    
    def __init__(self):
        if not self.GOOGLE_MAPS_API_KEY:
            raise ValueError("GOOGLE_MAPS_API_KEY environment variable is required")
        if not self.GOOGLE_MAPS_JS_API_KEY:
            raise ValueError("GOOGLE_MAPS_JS_API_KEY environment variable is required")

settings = Settings()