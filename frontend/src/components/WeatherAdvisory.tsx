import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  ArrowLeft, 
  Volume2, 
  CloudRain, 
  Sun, 
  Cloud, 
  Droplets,
  Wind,
  Thermometer,
  Eye,
  Loader2,
  MapPin,
  Calendar
} from 'lucide-react';
import { weatherAPI, WeatherData } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';

interface WeatherAdvisoryProps {
  onBack: () => void;
  selectedLanguage: string;
}

const WeatherAdvisory: React.FC<WeatherAdvisoryProps> = ({ onBack, selectedLanguage }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userLocation, setUserLocation] = useState<string>('Getting location...');
  const { t } = useTranslation();

  const handleVoiceOutput = () => {
    setIsPlaying(!isPlaying);
    setTimeout(() => setIsPlaying(false), 5000);
  };

  // Get user location and fetch weather data
  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Get user's current location
        const position = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000 // 5 minutes
          });
        });

        const { latitude, longitude } = position.coords;
        setUserLocation(`Lat: ${latitude.toFixed(4)}, Long: ${longitude.toFixed(4)}`);
        
        // Fetch weather data from API
        const data = await weatherAPI.getWeatherData(latitude, longitude);
        setWeatherData(data);
        
      } catch (err: any) {
        console.error('Error fetching weather data:', err);
        if (err.code === 1) {
          setError(t('error.locationDenied'));
        } else if (err.code === 2) {
          setError(t('error.locationUnavailable'));
        } else if (err.code === 3) {
          setError(t('error.locationTimeout'));
        } else {
          setError(t('error.failedToFetch'));
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchWeatherData();
  }, [t]);

  // Helper function to get weather icon based on weather code
  const getWeatherIcon = (weatherCode: number) => {
    if (weatherCode >= 0 && weatherCode <= 3) return <Sun className="h-5 w-5 text-blue-600" />;
    if (weatherCode >= 45 && weatherCode <= 48) return <Cloud className="h-5 w-5 text-blue-600" />;
    if (weatherCode >= 51 && weatherCode <= 67) return <CloudRain className="h-5 w-5 text-blue-600" />;
    if (weatherCode >= 71 && weatherCode <= 77) return <CloudRain className="h-5 w-5 text-blue-600" />;
    if (weatherCode >= 80 && weatherCode <= 99) return <CloudRain className="h-5 w-5 text-blue-600" />;
    return <Cloud className="h-5 w-5 text-blue-600" />;
  };

  return (
    <div className="min-h-screen bg-background p-4 max-w-md mx-auto pb-20">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="ghost"
          size="lg"
          onClick={onBack}
          className="p-2"
        >
          <ArrowLeft className="h-6 w-6" />
        </Button>
        
        <h1 className="text-xl font-bold text-primary">
          {t('weather.title')}
        </h1>
        
        <Button
          onClick={handleVoiceOutput}
          size="lg"
          variant="outline"
          className={`p-2 ${isPlaying ? 'bg-primary text-primary-foreground animate-pulse' : ''}`}
        >
          <Volume2 className="h-6 w-6" />
        </Button>
      </div>

            {/* Loading State */}
      {isLoading && (
        <Card className="mb-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-8 text-center">
            <Loader2 className="h-12 w-12 mx-auto text-blue-600 mb-4 animate-spin" />
            <p className="text-blue-800 font-medium mb-2">{t('weather.gettingData')}</p>
            <p className="text-sm text-blue-600">{userLocation}</p>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="mb-6 bg-red-50 border-red-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-red-800">
              <MapPin className="h-5 w-5" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Weather Card */}
      {weatherData && (
        <Card className="mb-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CloudRain className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="font-bold text-blue-800">{t('weather.currentWeather')}</p>
                  <p className="text-sm text-blue-700">{weatherData.weather_data.location.coordinates}</p>
                </div>
              </div>
              <div className="text-right">
                <Badge className="bg-blue-100 text-blue-800 border-blue-300">
                  {t('weather.liveData')}
                </Badge>
                <p className="text-xs text-blue-700 mt-1">
                  {t('weather.dataSource')}: {weatherData.data_quality.source}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Weather Details */}
      {weatherData && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Thermometer className="h-5 w-5" />
              {t('weather.currentConditions')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center mb-6">
              <div className="text-4xl font-bold text-blue-800 mb-2">
                {weatherData.weather_data.current.temperature}°C
              </div>
              <p className="text-lg font-medium text-blue-700 mb-1">
                {weatherData.weather_data.current.condition}
              </p>
              <p className="text-sm text-muted-foreground">
                {t('weather.feelsLike')} {weatherData.weather_data.current.apparent_temperature}°C
              </p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-2 p-3 rounded-lg border border-muted">
                <Droplets className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-xs text-muted-foreground">{t('weather.humidity')}</p>
                  <p className="font-medium">{weatherData.weather_data.current.humidity}%</p>
                </div>
              </div>
              
              <div className="flex items-center gap-2 p-3 rounded-lg border border-muted">
                <Wind className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-xs text-muted-foreground">{t('weather.wind')}</p>
                  <p className="font-medium">{weatherData.weather_data.current.wind_speed} km/h</p>
                </div>
              </div>
              
              <div className="flex items-center gap-2 p-3 rounded-lg border border-muted">
                <CloudRain className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-xs text-muted-foreground">{t('weather.rainChance')}</p>
                  <p className="font-medium">{weatherData.weather_data.current.rain_chance}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-2 p-3 rounded-lg border border-muted">
                <Eye className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-xs text-muted-foreground">{t('weather.visibility')}</p>
                  <p className="font-medium">{weatherData.weather_data.current.visibility}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 7-Day Forecast */}
      {weatherData && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              {weatherData.data_quality.forecast_days}-{t('weather.dayForecast')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {weatherData.weather_data.forecast.map((forecast, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg border border-muted">
                  <div className="flex items-center gap-3">
                    {getWeatherIcon(forecast.weather_code)}
                    <span className="font-medium">{forecast.day}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm font-medium">{forecast.temp}</span>
                    <Badge variant="secondary" className="text-xs">
                      {forecast.rain}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Agricultural Advisory */}
      {weatherData && (
        <Card className="mb-6 bg-green-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-lg text-green-800 flex items-center gap-2">
              <Sun className="h-5 w-5" />
              {t('weather.agriculturalAdvisory')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="p-4 rounded-lg bg-green-100/50 border border-green-200">
                <p className="font-medium text-green-800">
                  {weatherData.agricultural_advisory.recommendations}
                </p>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-green-700">
                  {weatherData.agricultural_advisory.ai_generated ? t('weather.aiGenerated') : t('weather.standardAdvisory')}
                </span>
                <span className="text-green-600">
                  {weatherData.agricultural_advisory.last_updated}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Data Quality Info */}
      {weatherData && (
        <Card className="mb-6 bg-gray-50 border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg text-gray-800 flex items-center gap-2">
              <Eye className="h-5 w-5" />
              {t('weather.dataQuality')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{t('weather.dataSource')}:</span>
                <span className="text-sm font-medium">{weatherData.data_quality.source}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{t('weather.forecastDays')}:</span>
                <span className="text-sm font-medium">{weatherData.data_quality.forecast_days}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{t('weather.hourlyData')}:</span>
                <span className="text-sm font-medium">{weatherData.data_quality.hourly_data_available ? t('weather.available') : t('weather.notAvailable')}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{t('weather.soilData')}:</span>
                <span className="text-sm font-medium">{weatherData.data_quality.soil_data_available ? t('weather.available') : t('weather.notAvailable')}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="space-y-3">
        {weatherData && (
          <Button 
            className="w-full h-12 text-lg"
            onClick={handleVoiceOutput}
          >
            <Volume2 className="h-5 w-5 mr-2" />
            {t('weather.listenToAdvisory')}
          </Button>
        )}
        
        <Button 
          variant="outline" 
          className="w-full h-12"
          onClick={onBack}
        >
          {t('weather.goBack')}
        </Button>
      </div>
    </div>
  );
};

export default WeatherAdvisory;