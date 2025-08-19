from fastapi import FastAPI, HTTPException, Depends, Request
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from app.models import LocationQuery, LocationResponse, DirectionsRequest, DirectionsResponse
from app.services.llm_service import LLMService
from app.services.maps_service import GoogleMapsService
from app.middleware import limiter, api_key_auth, SecurityHeaders, log_requests, rate_limit_handler
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Maps Finder",
    description="Find locations using natural language queries with local LLM and Google Maps",
    version="1.0.0"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Security middleware
app.middleware("http")(SecurityHeaders.add_security_headers)
app.middleware("http")(log_requests)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_service = LLMService()
maps_service = GoogleMapsService()

# Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main chat interface"""
    return templates.TemplateResponse(
        "chat_demo.html", 
        {
            "request": request,
            "GOOGLE_MAPS_JS_API_KEY": settings.GOOGLE_MAPS_JS_API_KEY
        }
    )

@app.post("/search", response_model=LocationResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
async def search_locations(request: Request, query: LocationQuery, auth: Optional[str] = Depends(api_key_auth)):
    """
    Main endpoint: Process natural language query to find locations
    """
    try:
        logger.info(f"Received query: {query.query}")
        
        # Step 1: Extract location intent using local LLM
        extracted_info = await llm_service.extract_location_intent(query.query)
        logger.info(f"Extracted info: {extracted_info}")
        
        # Step 2: Search Google Maps using extracted information
        formatted_query = extracted_info.get("formatted_query", query.query)
        locations = await maps_service.search_places(
            formatted_query, 
            user_location=query.user_location
        )
        
        # Calculate map center
        map_center = None
        if locations:
            # Use center of all locations
            avg_lat = sum(loc.lat for loc in locations) / len(locations)
            avg_lng = sum(loc.lng for loc in locations) / len(locations)
            map_center = {"lat": avg_lat, "lng": avg_lng}
        elif query.user_location:
            map_center = query.user_location
        
        if not locations:
            return LocationResponse(
                success=False,
                message="No locations found for your query",
                locations=[],
                extracted_info=extracted_info,
                map_center=map_center
            )
        
        return LocationResponse(
            success=True,
            message=f"Found {len(locations)} location(s)",
            locations=locations,
            extracted_info=extracted_info,
            map_center=map_center,
            search_radius=settings.MAPS_SEARCH_RADIUS
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your request: {str(e)}"
        )

@app.post("/directions", response_model=DirectionsResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
async def get_directions(request: Request, directions_request: DirectionsRequest, auth: Optional[str] = Depends(api_key_auth)):
    """
    Get directions between origin and destination
    """
    try:
        logger.info(f"Directions request: {directions_request.origin} to {directions_request.destination}")
        
        directions = await maps_service.get_directions(
            directions_request.origin,
            directions_request.destination,
            directions_request.travel_mode
        )
        
        return directions
        
    except Exception as e:
        logger.error(f"Error getting directions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting directions: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "ollama": settings.OLLAMA_BASE_URL,
            "google_maps": "configured" if settings.GOOGLE_MAPS_API_KEY else "not configured"
        },
        "rate_limits": {
            "requests_per_window": settings.RATE_LIMIT_REQUESTS,
            "window_seconds": settings.RATE_LIMIT_WINDOW
        }
    }


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat-like interface for LLM Maps interaction"""
    return templates.TemplateResponse(
        "chat_demo.html", 
        {
            "request": request,
            "GOOGLE_MAPS_JS_API_KEY": settings.GOOGLE_MAPS_JS_API_KEY
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)