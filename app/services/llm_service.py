import httpx
import json
from typing import Dict, Optional
from app.config import settings

class LLMService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        
    async def extract_location_intent(self, user_query: str) -> Dict:
        """Extract structured location information from user query using local LLM"""
        
        system_prompt = """You are a location extraction assistant. Extract location search information from user queries and return ONLY a valid JSON object with these exact fields:

{
  "search_term": "what the user is looking for (e.g., 'coffee shop', 'restaurant', 'hospital')",
  "location": "where to search (e.g., 'Taipei 101', 'downtown', 'near me')",
  "query_type": "search" or "directions",
  "formatted_query": "search_term + ' ' + location for Google Places API"
}

Examples:
User: "find a coffee shop near Taipei 101"
Response: {"search_term": "coffee shop", "location": "Taipei 101", "query_type": "search", "formatted_query": "coffee shop Taipei 101"}

User: "good beef noodles around here"
Response: {"search_term": "beef noodles", "location": "near me", "query_type": "search", "formatted_query": "beef noodles near me"}

Return ONLY the JSON object, no other text."""

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            "stream": False,
            "format": "json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                message_content = result["message"]["content"]
                
                # Parse the JSON response from LLM
                extracted_data = json.loads(message_content)
                
                # Validate required fields
                required_fields = ["search_term", "location", "query_type", "formatted_query"]
                if not all(field in extracted_data for field in required_fields):
                    raise ValueError("Missing required fields in LLM response")
                
                return extracted_data
                
        except json.JSONDecodeError as e:
            # Fallback: create basic extraction
            return {
                "search_term": user_query,
                "location": "near me",
                "query_type": "search",
                "formatted_query": user_query,
                "error": f"JSON parsing error: {str(e)}"
            }
        except Exception as e:
            return {
                "search_term": user_query,
                "location": "near me", 
                "query_type": "search",
                "formatted_query": user_query,
                "error": f"LLM service error: {str(e)}"
            }