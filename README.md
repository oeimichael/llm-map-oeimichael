# 🗺️ LLM Maps Finder

A powerful location discovery system that combines local Large Language Models with Google Maps to provide intelligent, natural language-based location search with embedded interactive maps.

## ✨ Features

### 🤖 AI-Powered Search
- **Natural Language Processing**: Use conversational queries like "find good coffee shops near Times Square"
- **Local LLM Integration**: Powered by Ollama for privacy-focused AI processing
- **Intent Extraction**: Automatically extracts search terms, locations, and query types

### 🗺️ Interactive Maps
- **Embedded Google Maps**: Interactive map with location markers and detailed info windows
- **Real-time Directions**: Get driving, walking, transit, and cycling directions via API
- **User Location Support**: Optional GPS-based location for proximity-based search results
- **Responsive Chat Interface**: Mobile-optimized chat interface that works on all devices

### 🔍 Rich Location Data
- **Comprehensive Information**: Ratings, price levels, opening hours, contact details
- **Distance Calculations**: Precise Haversine distance measurements
- **Multiple Results**: Up to 5 carefully curated location suggestions
- **Direct Integration**: Open results directly in Google Maps

### 🛡️ Enterprise Security
- **Rate Limiting**: Configurable request limits with in-memory storage
- **API Key Authentication**: Optional client authentication
- **Security Headers**: XSS protection, CSP, and CORS configuration
- **Request Logging**: Comprehensive monitoring and audit trails

### 🔌 Integration Ready
- **REST API**: Clean REST endpoints for search and directions
- **Chat Interface**: Interactive web-based chat for natural language queries
- **Environment Configuration**: Flexible configuration via environment variables

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) with a compatible model
- Google Cloud Account with Maps API access

### 1. Install UV Package Manager
```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

### 2. Clone and Install
```bash
git clone <repository-url>
cd llm-map

uv venv
.venv/scripts/activate #windows
source .venv/bin/activate #linux
uv pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Google Maps API keys
```

### 4. Set Up Google Cloud
Follow the detailed guide in [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md) to:
- Create a Google Cloud project
- Enable Maps APIs (Places, Directions, JavaScript Maps, Geocoding)
- Create and restrict API keys
- Set up billing and monitoring

### 5. Start Ollama
```bash
# Install and start Ollama
ollama pull gemma3:1b  # or your preferred model
ollama serve
```

### 6. Launch Application
```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Test the System
- Open `http://localhost:8000/` for the chat interface with embedded maps
- Visit `http://localhost:8000/health` to verify all services are running
- Try natural language queries like: "find Italian restaurants near downtown" or "coffee shops around here"

## 🛠️ Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GOOGLE_MAPS_API_KEY` | ✅ | Backend Google Maps API key | - |
| `GOOGLE_MAPS_JS_API_KEY` | ✅ | Frontend JavaScript API key | - |
| `OLLAMA_BASE_URL` | ❌ | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | ❌ | LLM model name | `gemma3:1b` |
| `ALLOWED_ORIGINS` | ❌ | CORS allowed origins | `localhost:*` |
| `RATE_LIMIT_REQUESTS` | ❌ | Requests per window | `100` |
| `RATE_LIMIT_WINDOW` | ❌ | Rate limit window (seconds) | `3600` |
| `MAX_LOCATIONS_RETURNED` | ❌ | Maximum search results | `5` |
| `MAPS_SEARCH_RADIUS` | ❌ | Search radius (meters) | `50000` |

### Security Configuration

#### API Key Setup
1. **Backend Key**: Restrict to server IP addresses and specific APIs
2. **Frontend Key**: Restrict to your domain and Maps JavaScript API only
3. **Never commit keys to version control**

#### Rate Limiting
- Default: 100 requests per hour per IP
- Uses in-memory storage

## 📡 API Reference

### Main Chat Interface
```http
GET /
```
Interactive chat interface with embedded Google Maps

### Search Locations
```http
POST /search
Content-Type: application/json

{
  "query": "find coffee shops near Central Park",
  "user_location": {
    "lat": 40.7829,
    "lng": -73.9654
  }
}
```

### Get Directions
```http
POST /directions
Content-Type: application/json

{
  "origin": {"lat": 40.7829, "lng": -73.9654},
  "destination": "Central Park",
  "travel_mode": "WALKING"
}
```

### Health Check
```http
GET /health
```
Returns detailed service status and configuration


## 🏗️ Architecture

### Core Components
- **`app/main.py`**: FastAPI application with security middleware, rate limiting, CORS, and REST endpoints
- **`app/services/llm_service.py`**: Ollama LLM integration for natural language processing of location queries  
- **`app/services/maps_service.py`**: Google Maps integration (Places API, Directions API, Geocoding)
- **`app/models.py`**: Pydantic data models for API requests and responses
- **`app/config.py`**: Environment-based configuration management
- **`app/middleware.py`**: Security middleware, rate limiting, API key authentication, and logging
- **`app/templates/chat_demo.html`**: Interactive frontend with embedded Google Maps

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat Frontend │    │   FastAPI       │    │   Ollama LLM    │
│   (HTML/JS)     │◄──►│   Backend       │◄──►│   Service       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐             │
         │              │   Google Maps   │             │
         └─────────────►│   APIs          │◄────────────┘
                        └─────────────────┘
```

### API Endpoints
- `GET /`: Chat interface with embedded Google Maps
- `GET /chat`: Alternative chat interface endpoint
- `GET /health`: Comprehensive health check with service status
- `POST /search`: Location search with natural language processing
- `POST /directions`: Get directions between two points with multiple travel modes

### Security Features
- **Rate Limiting**: In-memory rate limiting (configurable requests per hour)
- **API Key Authentication**: Optional client API key authentication
- **CORS Protection**: Configurable allowed origins
- **Security Headers**: CSP, XSS protection, frame options, content type validation
- **Request Logging**: Comprehensive request/response monitoring

### Data Flow
1. **User Input**: Natural language query via chat interface or REST API
2. **Intent Extraction**: Ollama LLM extracts structured location intent (search term, location, query type)
3. **Location Search**: Google Places API Text Search with location bias and radius filtering
4. **Data Enrichment**: Retrieve comprehensive location data (ratings, hours, contact info, price levels)
5. **Distance Calculation**: Haversine formula for precise distance measurements from user location
6. **Map Integration**: Calculate optimal map center and prepare markers for display
7. **Response**: Return structured data with interactive map display and Google Maps links

### External Dependencies
- **Ollama**: Local LLM server at `http://localhost:11434` (configurable model: gemma3:1b)
- **Google Maps APIs**: Places API (Text Search), Directions API, JavaScript Maps API, Geocoding API
- **Frontend Libraries**: No external JavaScript frameworks - uses vanilla JavaScript and Google Maps SDK

### Key Features
- **Privacy-First AI**: Local LLM processing without sending queries to external AI services
- **Real-time Search**: Fast location discovery with sub-second response times
- **Mobile Responsive**: Optimized chat interface that works on all device sizes
- **Rich Location Data**: Comprehensive business information including ratings, hours, and contact details
- **Interactive Maps**: Embedded Google Maps with markers, info windows, and directions support
- **Production Ready**: Built-in security, rate limiting, error handling, and monitoring

## 🧪 Testing

### Manual Testing
```bash
# Test search endpoint
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "find good sushi restaurants"}'

# Test directions endpoint  
curl -X POST "http://localhost:8000/directions" \
  -H "Content-Type: application/json" \
  -d '{"origin": {"lat": 40.7829, "lng": -73.9654}, "destination": "Central Park", "travel_mode": "WALKING"}'

# Test health endpoint
curl "http://localhost:8000/health"
```

### Integration Testing
- Open `http://localhost:8000/` for the main chat interface
- Test natural language queries like "find coffee shops near downtown"
- Verify location search, map display, and directions functionality
- Test rate limiting by making multiple rapid requests
- Check health endpoint at `http://localhost:8000/health`

## 🚢 Deployment


### Production Considerations
- Use environment-specific API keys
- Configure proper CORS origins
- Set up monitoring and logging
- Configure reverse proxy with SSL

### Monitoring
- Health check endpoint: `/health`
- Google Cloud Console for API usage
- Application logs for debugging

## 🛡️ Security Best Practices

### API Key Security
- Use separate keys for development and production
- Implement IP restrictions for backend keys
- Use HTTP referrer restrictions for frontend keys
- Rotate keys regularly
- Monitor usage in Google Cloud Console

### Application Security
- Enable rate limiting to prevent abuse
- Use HTTPS in production
- Implement proper CORS configuration
- Validate all input data
- Log security events
- Keep dependencies updated

### Data Privacy
- Minimize data collection
- Implement data retention policies
- Use local LLM for privacy-sensitive processing
- Follow GDPR and privacy regulations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive docstrings
- Include error handling
- Update tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM capabilities
- [Google Maps Platform](https://developers.google.com/maps) for mapping services
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

## 📞 Support

- 📚 Documentation: [Full API docs](http://localhost:8000/docs)
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)
- 📧 Email: your-email@example.com

---

**Happy mapping! 🗺️✨**