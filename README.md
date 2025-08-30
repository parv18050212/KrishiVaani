# KrishiVaani - Pest Detection System

A comprehensive pest detection system for farmers that uses AI to identify pests from images and provides treatment recommendations.

## Features

- 🐛 **AI-Powered Pest Detection**: Uses Perplexity AI to identify pests from crop images
- 💊 **Treatment Recommendations**: Provides specific treatment and pesticide recommendations
- 🌾 **Pesticide Database**: Includes a comprehensive database of pesticides for different pests
- 📱 **Mobile-Friendly UI**: Beautiful, responsive interface in Hindi and English
- 🔄 **Real-time Analysis**: Fast API backend for quick pest identification

## Project Structure

```
KrishiVaani/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── ...
├── pest/                    # Pest image dataset
├── api.py                   # FastAPI backend
├── pestNew.py              # Original Python script
├── Pesticides.csv          # Pesticide database
├── requirements.txt        # Python dependencies
└── start_backend.py        # Backend startup script
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- Perplexity AI API key (free at https://www.perplexity.ai/settings/api)

### 1. Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   perplexity_api=your_perplexity_api_key_here
   ```

3. **Start the backend server:**
   ```bash
   python start_backend.py
   ```
   
   The API will be available at:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### 2. Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at: http://localhost:5173

## API Endpoints

### POST /detect-pest
Upload an image to detect pests and get treatment recommendations.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Image file

**Response:**
```json
{
  "pestDetected": true,
  "pestName": "Aphids",
  "severity": "मध्यम / Medium",
  "confidence": "85%",
  "treatment": {
    "hindi": "नीम का तेल स्प्रे करें",
    "english": "Spray neem oil"
  },
  "pesticides": ["Imidacloprid", "Acetamiprid", "Thiamethoxam"],
  "prevention": {
    "hindi": "खेत को साफ रखें",
    "english": "Keep field clean"
  }
}
```

### GET /pesticides
Get the complete list of pests and their recommended pesticides.

### GET /health
Health check endpoint to verify API status.

## Usage

1. **Start both servers** (backend and frontend)
2. **Open the frontend** in your browser
3. **Navigate to Pest Detection** feature
4. **Upload an image** of a crop or pest
5. **View the analysis results** including:
   - Pest identification
   - Treatment recommendations
   - Recommended pesticides
   - Prevention tips

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Perplexity AI**: AI-powered pest identification
- **Pandas**: Data processing for pesticide database
- **Python-multipart**: File upload handling

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **Radix UI**: Accessible components
- **Vite**: Build tool

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue on GitHub.
