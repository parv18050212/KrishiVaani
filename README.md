# 🌾 KrishiVaani - AI-Powered Agricultural Advisory Platform

KrishiVaani is a comprehensive agricultural advisory platform designed for Indian farmers. It leverages advanced AI (Perplexity Sonar Pro) with LangGraph agents to provide real-time weather information, pest detection, market prices, soil analysis, and intelligent farming advice through voice and text.

## 🚀 Features

### 🤖 Agentic AI Assistant
- **LangGraph-powered agent** with tool-calling capabilities
- **Perplexity Sonar Pro** for intelligent responses
- Voice-enabled chat with speech-to-text
- Conversation memory and rollback support
- Multi-language support for Indian farmers

### 🌤️ Weather Advisory
- Real-time weather forecasts using Open-Meteo API
- Agricultural-specific weather insights
- Crop-specific weather recommendations
- Soil temperature and moisture analysis

### 🐛 Pest Detection
- AI-powered image-based pest identification
- Treatment recommendations with confidence scoring
- Comprehensive pesticide database
- Multi-language pest information

### 🌱 Soil Analysis
- Soil health card OCR analysis
- AI-powered fertilizer recommendations
- Crop-specific nutrient management
- NPK ratio suggestions

### 📊 Market Prices
- Real-time mandi (market) prices
- Location-based market insights
- Price trend analysis
- Multi-language market information

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│                    http://localhost:3000                    │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼───────────────────────────────────────┐
│                 Unified Backend (FastAPI)                   │
│                   http://localhost:8000                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    main.py                          │    │
│  │  - /chat/* endpoints (uses backend/agent.py)        │    │
│  │  - Imports routers from backend modules             │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                 │
│  ┌────────────┬───────────┼───────────┬────────────────┐    │
│  │            │           │           │                │    │
│  ▼            ▼           ▼           ▼                ▼    │
│ agent.py   weather.py   pest.py   market.py        soil.py  │
│ (LangGraph) (Open-Meteo) (Perplexity) (Mandi API) (OCR)     │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
KrishiVaani/
├── main.py                   # Unified FastAPI server (entry point)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── backend/                  # Backend modules
│   ├── agent.py             # LangGraph AI agent (Perplexity Sonar Pro)
│   ├── weather.py           # Weather API service
│   ├── pest.py              # Pest detection service
│   ├── market.py            # Market prices service
│   ├── soil.py              # Soil analysis service
│   ├── Pesticides.csv       # Pesticide database
│   └── .env                 # Backend-specific env vars
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── services/        # API services
│   │   └── hooks/           # Custom React hooks
│   ├── .env                 # Frontend env (VITE_BACKEND_URL)
│   ├── package.json
│   └── vite.config.ts
├── localBackend/            # Alternative local services
└── pest/                    # Pest image dataset
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - High-performance web framework
- **LangChain + LangGraph** - Agentic AI framework
- **Perplexity Sonar Pro** - Primary AI model
- **Python 3.8+** - Programming language
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Web Speech API** - Voice input

### External APIs
- **Perplexity AI** - Chat and pest detection
- **Open-Meteo** - Weather data
- **Government Mandi API** - Market prices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 1. Clone & Setup Environment

```bash
git clone <repository-url>
cd KrishiVaani

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `backend/.env`:
```env
PERPLEXITY_API_KEY=your_perplexity_api_key

# Optional: Override service URLs
WEATHER_API_URL=http://localhost:8000
PEST_API_URL=http://localhost:8000
MARKET_API_URL=http://localhost:8000
```

Create `frontend/.env`:
```env
VITE_BACKEND_URL=http://127.0.0.1:8000
```

### 3. Start the Backend

```bash
# From project root
python main.py
```

Backend will start at `http://localhost:8000`

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will start at `http://localhost:3000`

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | AI chat with agentic tools |
| `/chat/speech` | POST | Optimized for voice queries |
| `/chat/rollback/{session_id}` | POST | Rollback conversation state |
| `/api/weather` | POST | Get weather advisory |
| `/api/pest/detect` | POST | Detect pest from image |
| `/api/market/prices` | POST | Get mandi prices |
| `/api/soil/analyze` | POST | Analyze soil health card |
| `/health` | GET | System health check |

### Chat Request Example

```json
POST /chat
{
  "query": "What is the best time to sow wheat in Punjab?",
  "session_id": "optional-session-id",
  "language": "en",
  "location": "Punjab",
  "crop": "wheat"
}
```

### Chat Response Example

```json
{
  "answer": "The best time to sow wheat in Punjab is...",
  "session_id": "session_20251226_123456_abc123",
  "has_context": true,
  "tools_used": ["get_crop_calendar"],
  "sources": []
}
```

## 🔧 Agent Tools

The LangGraph agent has access to these tools:

| Tool | Description |
|------|-------------|
| `get_weather_advisory` | Fetch weather data and farming advice |
| `get_pest_information` | Get pest details and treatment |
| `get_market_prices` | Fetch current mandi prices |
| `get_fertilizer_recommendation` | Crop-specific fertilizer advice |
| `get_crop_calendar` | Sowing/harvesting schedules |
| `general_agriculture_query` | General farming questions |

## 🌍 Multi-Language Support

KrishiVaani supports queries in multiple Indian languages. The AI will respond in the same language as the query.

Supported features:
- Hindi, Punjabi, Tamil, Telugu, and more
- Voice input via Web Speech API (Chrome recommended)
- Localized agricultural terminology

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Perplexity AI** - AI chat capabilities
- **Open-Meteo** - Weather data API
- **LangChain/LangGraph** - Agent framework
- **Government of India** - Mandi price data

---

**KrishiVaani** - Empowering Indian farmers with AI-driven agricultural insights 🌾✨
