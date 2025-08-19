import httpx
import math
from typing import List, Dict, Optional, Any
from app.config import settings
from app.models import LocationInfo, DirectionsResponse

class GoogleMapsService:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def search_places(self, query: str, location_bias: Optional[str] = None, user_location: Optional[Dict[str, float]] = None) -> List[LocationInfo]:
        """Search for places using Google Places API Text Search"""
        
        # Use Places API (New) Text Search
        url = f"{self.base_url}/place/textsearch/json"
        
        params = {
            "query": query,
            "key": self.api_key,
            "fields": "place_id,name,formatted_address,geometry,rating,opening_hours,international_phone_number,website,price_level"
        }
        
        # Add location bias for better local results
        if user_location:
            params["location"] = f"{user_location['lat']},{user_location['lng']}"
            params["radius"] = settings.MAPS_SEARCH_RADIUS
        elif location_bias and location_bias.lower() != "near me":
            params["locationbias"] = f"point:{location_bias}"
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data["status"] != "OK":
                    raise Exception(f"Google Places API error: {data.get('status', 'Unknown error')}")
                
                locations = []
                
                # Process up to configured max results
                for place in data.get("results", [])[:settings.MAX_LOCATIONS_RETURNED]:
                    place_lat = place["geometry"]["location"]["lat"]
                    place_lng = place["geometry"]["location"]["lng"]
                    
                    # Calculate distance if user location is provided
                    distance = None
                    if user_location:
                        distance = self._calculate_distance(
                            user_location["lat"], user_location["lng"],
                            place_lat, place_lng
                        )
                    
                    location_info = LocationInfo(
                        name=place.get("name", "Unknown"),
                        address=place.get("formatted_address", "Address not available"),
                        place_id=place.get("place_id", ""),
                        rating=place.get("rating"),
                        lat=place_lat,
                        lng=place_lng,
                        distance=distance,
                        opening_hours=place.get("opening_hours", {}).get("weekday_text"),
                        phone_number=place.get("international_phone_number"),
                        website=place.get("website"),
                        price_level=place.get("price_level"),
                        maps_url=self._generate_maps_url(
                            place.get("place_id", ""),
                            place_lat,
                            place_lng
                        )
                    )
                    locations.append(location_info)
                
                return locations
                
        except Exception as e:
            raise Exception(f"Error searching places: {str(e)}")
    
    def _generate_maps_url(self, place_id: str, lat: float, lng: float) -> str:
        """Generate Google Maps URL for the location"""
        if place_id:
            return f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        else:
            return f"https://www.google.com/maps/@{lat},{lng},15z"
    
    async def geocode_address(self, address: str) -> Optional[Dict]:
        """Geocode an address to get coordinates (fallback method)"""
        url = f"{self.base_url}/geocode/json"
        
        params = {
            "address": address,
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data["status"] == "OK" and data["results"]:
                    result = data["results"][0]
                    return {
                        "lat": result["geometry"]["location"]["lat"],
                        "lng": result["geometry"]["location"]["lng"],
                        "formatted_address": result["formatted_address"]
                    }
                
                return None
                
        except Exception:
            return None
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula (returns meters)"""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) * math.sin(delta_lng / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    async def get_directions(self, origin: Dict[str, float], destination: str, travel_mode: str = "DRIVING") -> DirectionsResponse:
        """Get directions between origin and destination"""
        url = f"{self.base_url}/directions/json"
        
        params = {
            "origin": f"{origin['lat']},{origin['lng']}",
            "destination": destination,
            "mode": travel_mode.lower(),
            "key": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data["status"] != "OK":
                    return DirectionsResponse(
                        success=False,
                        message=f"Directions API error: {data.get('status', 'Unknown error')}"
                    )
                
                if not data.get("routes"):
                    return DirectionsResponse(
                        success=False,
                        message="No routes found"
                    )
                
                route = data["routes"][0]
                leg = route["legs"][0]
                
                return DirectionsResponse(
                    success=True,
                    message="Directions found",
                    routes=data["routes"],
                    duration=leg["duration"]["text"],
                    distance=leg["distance"]["text"]
                )
                
        except Exception as e:
            return DirectionsResponse(
                success=False,
                message=f"Error getting directions: {str(e)}"
            )