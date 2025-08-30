# KrishiVaani - Agricultural Advisory Platform

A comprehensive agricultural advisory platform with pest detection, weather forecasting, and market price analysis.

## 🚀 Features

- **Pest Detection**: AI-powered pest identification with treatment recommendations
- **Weather Advisory**: Real-time weather data with agricultural recommendations
- **Market Prices**: Location-based market price analysis and trends
- **Fertilizer Planning**: Crop-specific fertilizer recommendations
- **Modern UI**: Responsive React frontend with beautiful design

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Google AI API key (for pest detection and weather advisory)
- Perplexity AI API key (for market price analysis)

## 🛠️ Setup Instructions

### 1. Environment Variables

Create a `.env` file in the root directory:

```env
# For Pest Detection and Weather Advisory
api=your_google_ai_api_key_here

# For Market Price Analysis
perplexity_api=your_perplexity_api_key_here
```

**Get API Keys:**
- Google AI: https://makersuite.google.com/app/apikey
- Perplexity AI: https://www.perplexity.ai/settings/api

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install fastapi uvicorn python-multipart openai python-dotenv openmeteo-requests geocoder requests-cache retry-requests geopy pandas

# Install frontend dependencies
cd frontend
npm install
```

### 3. Start the Backend APIs

**Pest Detection API (Port 8000):**
```bash
python start_backend.py
```

**Weather API (Port 8001):**
```bash
python start_weather_api.py
```

**Market API (Port 8002):**
```bash
python start_market_api.py
```

### 4. Start the Frontend

```bash
cd frontend
npm run dev
```

## 🌐 API Endpoints

### Pest Detection API (Port 8000)
- `POST /detect-pest` - Detect pests from uploaded images
- `GET /pesticides` - Get list of pesticides
- `GET /health` - Health check

### Weather API (Port 8001)
- `POST /weather` - Get weather data and agricultural advisory
- `GET /health` - Health check

### Market API (Port 8002)
- `POST /market-prices` - Get market price analysis
- `GET /health` - Health check

## 📱 Frontend Features

### Dashboard
- Navigation to all features
- Status indicators
- Modern card-based layout

### Pest Detection
- Image upload (camera/gallery)
- AI-powered pest identification
- Treatment and prevention recommendations
- Pesticide suggestions

### Weather Advisory
- Real-time weather data
- 7-day forecast
- Agricultural recommendations
- Location-based analysis

### Market Prices
- Location-based market analysis
- Price trends and comparisons
- Trading recommendations
- Market status information

### Fertilizer Plan
- Crop-specific recommendations
- Application timing
- Dosage information
- Soil health insights

## 🔧 Technology Stack

**Backend:**
- FastAPI (Python)
- OpenAI/Google AI APIs
- Open-Meteo API
- Geopy for geocoding
- Pandas for data processing

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Radix UI Components
- Axios for API calls

## 📁 Project Structure

```
KrishiVaani/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── styles/          # CSS styles
│   └── package.json
├── pest/                    # Pest image dataset
├── api.py                   # Pest detection API
├── weather_api.py           # Weather API
├── market_api.py            # Market price API
├── start_*.py              # Startup scripts
├── requirements.txt         # Python dependencies
└── README.md
```

## 🚀 Quick Start

1. **Clone and setup:**
```bash
git clone <repository-url>
cd KrishiVaani
```

2. **Create .env file with your API keys**

3. **Install dependencies:**
```bash
pip install -r requirements.txt
cd frontend && npm install
```

4. **Start all services:**
```bash
# Terminal 1 - Pest API
python start_backend.py

# Terminal 2 - Weather API  
python start_weather_api.py

# Terminal 3 - Market API
python start_market_api.py

# Terminal 4 - Frontend
cd frontend && npm run dev
```

5. **Open browser:**
- Frontend: http://localhost:3000
- Pest API Docs: http://localhost:8000/docs
- Weather API Docs: http://localhost:8001/docs
- Market API Docs: http://localhost:8002/docs

## 🔍 API Documentation

Each API provides interactive documentation at `/docs` endpoint when running.

### Example API Calls

**Pest Detection:**
```bash
curl -X POST "http://localhost:8000/detect-pest" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@pest_image.jpg"
```

**Weather Data:**
```bash
curl -X POST "http://localhost:8001/weather" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 27.5035, "longitude": 77.6722}'
```

**Market Prices:**
```bash
curl -X POST "http://localhost:8002/market-prices" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 27.5035, "longitude": 77.6722}'
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   - Check if other services are running on ports 8000, 8001, 8002
   - Kill processes or change ports in startup scripts

2. **API key errors:**
   - Ensure `.env` file exists with correct API keys
   - Check API key validity and quotas

3. **Location access denied:**
   - Enable location services in browser
   - Allow location access when prompted

4. **CORS errors:**
   - APIs are configured to allow all origins for development
   - Check if APIs are running on correct ports

### Logs

Check terminal outputs for detailed error messages and API logs.

## 📄 License

This project is for educational and agricultural advisory purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions, please check the troubleshooting section or create an issue in the repository.
