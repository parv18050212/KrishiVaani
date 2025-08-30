import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
const WEATHER_API_BASE_URL = 'http://localhost:8001';
const MARKET_API_BASE_URL = 'http://localhost:8002';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface PestDetectionResult {
  pestDetected: boolean;
  pestName: string;
  severity: string;
  confidence: string;
  confidenceBreakdown?: {
    image_quality: string;
    pest_name_match: string;
    pesticide_availability: string;
    response_consistency: string;
  };
  confidenceFactors?: {
    image_size_adequate: boolean;
    pest_in_database: boolean;
    pesticides_available: boolean;
    response_consistent: boolean;
  };
  treatment: {
    hindi: string;
    english: string;
  };
  pesticides: string[];
  prevention: {
    hindi: string;
    english: string;
  };
}

export interface PesticideInfo {
  'Pest Name': string;
  'Most Commonly Used Pesticides': string;
}

export const pestDetectionAPI = {
  // Detect pest from image
  detectPest: async (imageFile: File): Promise<PestDetectionResult> => {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    const response = await api.post('/detect-pest', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Get all pesticides data
  getPesticides: async (): Promise<PesticideInfo[]> => {
    const response = await api.get('/pesticides');
    return response.data.pesticides;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export interface WeatherData {
  current: {
    temperature: number;
    condition: string;
    humidity: number;
    wind_speed: number;
    visibility: string;
    rain_chance: string;
  };
  forecast: Array<{
    day: string;
    temp: string;
    rain: string;
    weather_code: number;
  }>;
  advisory: string;
  location: string;
}

// Create separate axios instance for weather API
const weatherApi = axios.create({
  baseURL: WEATHER_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const weatherAPI = {
  // Get weather data for coordinates
  getWeatherData: async (latitude: number, longitude: number): Promise<WeatherData> => {
    const response = await weatherApi.post('/weather', {
      latitude,
      longitude
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await weatherApi.get('/health');
    return response.data;
  },
};

export interface MarketData {
  location: {
    district: string;
    state: string;
    coordinates: string;
  };
  current_prices: Array<{
    crop: string;
    current_price: string;
    yesterday_price: string;
    trend: 'up' | 'down';
    change: string;
    unit: string;
  }>;
  nearby_mandis: Array<{
    name: string;
    distance: string;
    status: string;
    timing: string;
  }>;
  recommendations: string;
  last_updated: string;
}

// Create separate axios instance for market API
const marketApi = axios.create({
  baseURL: MARKET_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const marketAPI = {
  // Get market prices for coordinates
  getMarketPrices: async (latitude: number, longitude: number): Promise<MarketData> => {
    const response = await marketApi.post('/market-prices', {
      latitude,
      longitude
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await marketApi.get('/health');
    return response.data;
  },
};

export default api;
