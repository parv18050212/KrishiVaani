import axios from 'axios';

const API_BASE_URL = 'http://43.204.140.241:8000';
const WEATHER_API_BASE_URL = 'http://43.204.140.241:8001';
const MARKET_API_BASE_URL = 'http://43.204.140.241:8002';
const OCR_API_BASE_URL = 'http://43.204.140.241:8003';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface PestDetectionResult {
  pest_detection: {
    detected: boolean;
    pest_name: string;
    severity: string;
    confidence: string;
    confidence_score: number;
    confidence_breakdown: {
      image_quality: string;
      pest_name_match: string;
      pesticide_availability: string;
      response_consistency: string;
    };
    confidence_factors: {
      image_size_adequate: boolean;
      pest_in_database: boolean;
      pesticides_available: boolean;
      response_consistent: boolean;
    };
  };
  treatment: {
    recommendations: {
      english: string;
    };
    pesticides: string[];
    prevention: {
      english: string;
    };
  };
  analysis: {
    image_processed: boolean;
    ai_model_used: string;
    processing_time: string;
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
  weather_data: {
    current: {
      temperature: number;
      condition: string;
      humidity: number;
      wind_speed: number;
      visibility: string;
      rain_chance: string;
      apparent_temperature: number;
      cloud_cover: number;
    };
    forecast: Array<{
      day: string;
      temp: string;
      rain: string;
      weather_code: number;
    }>;
    location: {
      coordinates: string;
      latitude: number;
      longitude: number;
    };
  };
  agricultural_advisory: {
    recommendations: string;
    ai_generated: boolean;
    last_updated: string;
  };
  data_quality: {
    source: string;
    forecast_days: number;
    hourly_data_available: boolean;
    soil_data_available: boolean;
  };
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
  market_data: {
    location: {
      district: string;
      state: string;
      coordinates: string;
      latitude: number;
      longitude: number;
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
  };
  recommendations: {
    trading_advice: string;
    ai_generated: boolean;
    last_updated: string;
  };
  data_quality: {
    source: string;
    geocoding_used: boolean;
    real_time_data: boolean;
  };
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

// Create separate axios instance for OCR API
const ocrApi = axios.create({
  baseURL: OCR_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SoilAnalysisResult {
  status: string;
  soil_health: {
    nitrogen: {
      value: string;
      level: string;
      percentage: number;
    };
    phosphorus: {
      value: string;
      level: string;
      percentage: number;
    };
    potassium: {
      value: string;
      level: string;
      percentage: number;
    };
    ph: {
      value: string;
      level: string;
      percentage: number;
    };
  };
  fertilizer_plan: {
    crop_data: {
      name: string;
      stage: string;
      progress: number;
      nextFertilizer: string;
    };
    current_plan: Array<{
      fertilizer: string;
      amount: string;
      timing: string;
      method: string;
      status: string;
      priority: string;
    }>;
    recommendations: {
      english: string;
    };
  };
}

export const fertilizerAPI = {
  // Analyze soil health card image
  analyzeSoil: async (imageFile: File): Promise<SoilAnalysisResult> => {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    const response = await ocrApi.post('/analyze-soil', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await ocrApi.get('/health');
    return response.data;
  },
};

export default api;
