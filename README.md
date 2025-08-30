# 🌾 KrishiVaani - Farmer-Friendly Crop Advisory Mobile App

KrishiVaani is a comprehensive agricultural advisory platform that leverages AI and machine learning to provide farmers with real-time weather information, pest detection, fertilizer recommendations, and market price insights. The application is designed to be accessible in multiple languages and provides a user-friendly interface for farmers to make informed agricultural decisions.

## 🚀 Features

### 🌤️ Weather Advisory
- Real-time weather forecasts using Open-Meteo API
- Agricultural-specific weather insights
- Soil temperature and moisture monitoring
- UV index and wind speed analysis
- AI-powered crop-specific weather recommendations

### 🐛 Pest Detection
- Image-based pest identification using AI
- Treatment recommendations with confidence scoring
- Comprehensive pesticide database
- Image quality assessment for better accuracy
- Multi-language support for pest information

### 🌱 Fertilizer Planning
- AI-powered fertilizer recommendations
- Crop-specific nutrient management
- Soil health analysis
- Seasonal fertilizer planning
- Cost-effective fertilizer suggestions

### 📊 Market Price Analysis
- Real-time agricultural commodity prices
- Location-based market insights
- Price trend analysis
- Market forecasting using AI
- Multi-language market information

### 💬 AI Chat Assistant (RAG)
- Retrieval-Augmented Generation (RAG) powered chat
- Context-aware agricultural advice
- Integration with Supabase vector database
- Gemini AI embeddings for semantic search
- Perplexity AI for enhanced responses

### 🌍 Multi-Language Support
- Support for multiple Indian languages
- Voice-to-text capabilities
- Localized agricultural terminology
- Cultural context-aware recommendations

## 🏗️ Architecture

The project follows a modern microservices architecture with:

- **Frontend**: React + TypeScript + Vite
- **Backend APIs**: FastAPI (Python)
- **AI Services**: Google Gemini, Perplexity AI
- **Database**: Supabase (PostgreSQL + Vector Store)
- **UI Components**: Radix UI + Tailwind CSS

## 📁 Project Structure

```
KrishiVaani/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── services/         # API services
│   │   ├── hooks/           # Custom React hooks
│   │   └── styles/          # CSS styles
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # FastAPI microservices
│   ├── weather_api.py       # Weather advisory service
│   ├── pest_api.py          # Pest detection service
│   ├── market_api.py        # Market price service
│   ├── ocr.py              # OCR service
│   ├── requirements.txt
│   └── Pesticides.csv      # Pest database
├── localBackend/            # Local development services
├── main.py                  # RAG chat API
├── ingest.py               # Data ingestion script
└── pest/                   # Pest image dataset
```

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Radix UI** - Accessible UI components
- **Axios** - HTTP client
- **React Hook Form** - Form management

### Backend
- **FastAPI** - Web framework
- **Python 3.8+** - Programming language
- **Uvicorn** - ASGI server
- **Pandas** - Data manipulation
- **Pillow** - Image processing
- **OpenAI** - AI client (Perplexity/Gemini)

### AI & ML
- **Google Gemini** - Embeddings and AI responses
- **Perplexity AI** - Enhanced AI responses
- **Supabase** - Vector database and storage
- **Open-Meteo** - Weather data API

### Development Tools
- **Git** - Version control
- **Python venv** - Virtual environment
- **npm** - Package management

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Git

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd KrishiVaani
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Set up frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_TABLE=rag_documents

   # AI API Keys
   GEMINI_API_KEY=your_gemini_api_key
   PERPLEXITY_API_KEY=your_perplexity_api_key

   # Weather API
   api=your_weather_api_key

   # Optional: OCR API
   OCR_API_KEY=your_ocr_api_key
   ```

### Running the Application

1. **Start the RAG Chat API**
   ```bash
   python main.py
   ```

2. **Start Weather API**
   ```bash
   cd backend
   python start_weather_api.py
   ```

3. **Start Pest Detection API**
   ```bash
   cd backend
   python start_pest_api.py
   ```

4. **Start Market API**
   ```bash
   cd backend
   python start_market_api.py
   ```

5. **Start Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## 📚 API Documentation

### RAG Chat API (`main.py`)
- **POST** `/chat` - Chat with AI assistant
- **POST** `/stream-chat` - Streaming chat responses
- **POST** `/ingest` - Ingest documents into vector store

### Weather API (`weather_api.py`)
- **GET** `/health` - Health check
- **POST** `/weather` - Get weather data and advisory

### Pest Detection API (`pest_api.py`)
- **GET** `/health` - Health check
- **POST** `/detect-pest` - Detect pests from image
- **GET** `/pesticides` - Get pesticide information

### Market API (`market_api.py`)
- **GET** `/health` - Health check
- **POST** `/market-prices` - Get market prices

## 🔧 Development

### Adding New Features
1. Create new components in `frontend/src/components/`
2. Add corresponding API endpoints in backend services
3. Update routing in `App.tsx`
4. Add translations for new features

### Code Style
- Frontend: ESLint + Prettier
- Backend: Black + Flake8
- TypeScript strict mode enabled
- Python type hints required

### Testing
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
python -m pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Open-Meteo** for weather data
- **Google Gemini** for AI capabilities
- **Perplexity AI** for enhanced responses
- **Supabase** for database and vector storage
- **Radix UI** for accessible components
- **Tailwind CSS** for styling

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation in the `docs/` folder

---

**KrishiVaani** - Empowering farmers with AI-driven agricultural insights 🌾✨
