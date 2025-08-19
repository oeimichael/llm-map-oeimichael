from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class LocationQuery(BaseModel):
    query: str
    user_location: Optional[Dict[str, float]] = None  # {"lat": 40.7128, "lng": -74.0060}

class LocationInfo(BaseModel):
    name: str
    address: str
    place_id: str
    rating: Optional[float] = None
    maps_url: str
    lat: float
    lng: float
    distance: Optional[float] = None  # Distance in meters from user location
    opening_hours: Optional[List[str]] = None
    phone_number: Optional[str] = None
    website: Optional[str] = None
    price_level: Optional[int] = None  # 0-4 scale

class DirectionsRequest(BaseModel):
    origin: Dict[str, float]  # {"lat": 40.7128, "lng": -74.0060}
    destination: str  # place_id or address
    travel_mode: Optional[str] = "DRIVING"  # DRIVING, WALKING, TRANSIT, BICYCLING

class DirectionsResponse(BaseModel):
    success: bool
    message: str
    routes: Optional[List[Dict[str, Any]]] = None
    duration: Optional[str] = None
    distance: Optional[str] = None

class LocationResponse(BaseModel):
    success: bool
    message: str
    locations: List[LocationInfo] = []
    extracted_info: Optional[dict] = None
    map_center: Optional[Dict[str, float]] = None
    search_radius: Optional[int] = None