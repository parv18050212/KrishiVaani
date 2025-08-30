import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  ArrowLeft, 
  Volume2, 
  IndianRupee, 
  TrendingUp, 
  TrendingDown,
  MapPin,
  Calendar,
  BarChart3,
  Store,
  Loader2,
  Eye
} from 'lucide-react';
import { marketAPI, MarketData } from '../services/api';

interface MarketPriceProps {
  onBack: () => void;
}

const MarketPrice: React.FC<MarketPriceProps> = ({ onBack }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleVoiceOutput = () => {
    setIsPlaying(!isPlaying);
    setTimeout(() => setIsPlaying(false), 5000);
  };

  // Get user location and fetch market data
  useEffect(() => {
    const fetchMarketData = async () => {
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
        
        // Fetch market data from API
        const data = await marketAPI.getMarketPrices(latitude, longitude);
        setMarketData(data);
        
      } catch (err: any) {
        console.error('Error fetching market data:', err);
        if (err.code === 1) {
          setError('Location access denied. Please enable location services.');
        } else if (err.code === 2) {
          setError('Location unavailable. Please check your connection.');
        } else if (err.code === 3) {
          setError('Location request timed out. Please try again.');
        } else {
          setError('Failed to fetch market data. Please try again.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchMarketData();
  }, []);

  return (
    <div className="min-h-screen bg-background p-4 max-w-md mx-auto">
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
          Market Prices
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
        <Card className="mb-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
          <CardContent className="p-8 text-center">
            <Loader2 className="h-12 w-12 mx-auto text-yellow-600 mb-4 animate-spin" />
            <p className="text-yellow-800 font-medium mb-2">Getting Market Data</p>
            <p className="text-sm text-yellow-600">Fetching prices for your location...</p>
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

      {/* Market Info */}
      {marketData && (
        <Card className="mb-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-yellow-600" />
                <div>
                  <p className="font-bold text-yellow-800">{marketData.market_data.location.district}</p>
                  <p className="text-sm text-yellow-700">{marketData.market_data.location.state}</p>
                </div>
              </div>
              <div className="text-right">
                <Badge className="bg-green-100 text-green-800 border-green-300">
                  Market Open
                </Badge>
                <p className="text-xs text-yellow-700 mt-1">
                  Source: {marketData.data_quality.source}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Prices */}
      {marketData && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <IndianRupee className="h-5 w-5" />
              Today's Rates
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {marketData.market_data.current_prices.map((item, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-4 rounded-lg border border-muted"
                >
                  <div>
                    <p className="font-bold text-lg">
                      {item.crop}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {item.unit}
                    </p>
                  </div>
                  
                  <div className="text-right">
                    <div className="flex items-center gap-2">
                      <p className="font-bold text-xl">
                        ₹{item.current_price}
                      </p>
                      <div className={`flex items-center gap-1 ${
                        item.trend === 'up' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {item.trend === 'up' ? (
                          <TrendingUp className="h-4 w-4" />
                        ) : (
                          <TrendingDown className="h-4 w-4" />
                        )}
                        <span className="text-sm font-medium">
                          {item.change}
                        </span>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Yesterday: ₹{item.yesterday_price}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Nearby Markets */}
      {marketData && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Store className="h-5 w-5" />
              Nearby Markets
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {marketData.market_data.nearby_mandis.map((market, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/30"
                >
                  <div>
                    <p className="font-medium">
                      {market.name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {market.distance} away
                    </p>
                  </div>
                  
                  <div className="text-right">
                    <Badge className="bg-green-100 text-green-800 border-green-300 mb-1">
                      {market.status}
                    </Badge>
                    <p className="text-xs text-muted-foreground">
                      {market.timing}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Price Recommendations */}
      {marketData && (
        <Card className="mb-6 bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-lg text-blue-800 flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Trading Advice
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="p-4 rounded-lg bg-blue-100/50 border border-blue-200">
                <p className="font-medium text-blue-800">
                  {marketData.recommendations.trading_advice}
                </p>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-blue-700">
                  {marketData.recommendations.ai_generated ? 'AI Generated' : 'Standard Advice'}
                </span>
                <span className="text-blue-600">
                  {marketData.recommendations.last_updated}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Weekly Trend Info */}
      {marketData && (
        <Card className="mb-6 bg-green-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-lg text-green-800 flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Weekly Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {marketData.market_data.current_prices.slice(0, 3).map((item, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm">{item.crop}</span>
                  <div className="flex items-center gap-1 text-green-600">
                    {item.trend === 'up' ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : (
                      <TrendingDown className="h-4 w-4" />
                    )}
                    <span className="text-sm font-medium">{item.change}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Data Quality Info */}
      {marketData && (
        <Card className="mb-6 bg-gray-50 border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg text-gray-800 flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Data Quality
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Data Source:</span>
                <span className="text-sm font-medium">{marketData.data_quality.source}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Geocoding:</span>
                <span className="text-sm font-medium">{marketData.data_quality.geocoding_used ? 'Used' : 'Not Used'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Real-time:</span>
                <span className="text-sm font-medium">{marketData.data_quality.real_time_data ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="space-y-3">
        {marketData && (
          <Button 
            className="w-full h-12 text-lg"
            onClick={handleVoiceOutput}
          >
            <Volume2 className="h-5 w-5 mr-2" />
            Listen to Market Analysis
          </Button>
        )}
        
        <Button 
          variant="outline" 
          className="w-full h-12"
          onClick={onBack}
        >
          Go Back
        </Button>
      </div>
    </div>
  );
};

export default MarketPrice;