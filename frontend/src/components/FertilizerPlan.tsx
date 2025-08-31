import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  ArrowLeft, 
  Volume2, 
  Package, 
  Calendar, 
  Droplets,
  Leaf,
  TrendingUp,
  Clock,
  AlertCircle,
  Upload,
  Camera
} from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';
import { fertilizerAPI, SoilAnalysisResult } from '../services/api';

interface FertilizerPlanProps {
  onBack: () => void;
  selectedLanguage: string;
}

const FertilizerPlan: React.FC<FertilizerPlanProps> = ({ onBack, selectedLanguage }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedCrop, setSelectedCrop] = useState('wheat');
  const [isLoading, setIsLoading] = useState(false);
  const [soilData, setSoilData] = useState<SoilAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { t } = useTranslation();

  const handleVoiceOutput = () => {
    setIsPlaying(!isPlaying);
    setTimeout(() => setIsPlaying(false), 5000);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await fertilizerAPI.analyzeSoil(file);
      setSoilData(result);
    } catch (err) {
      setError('Failed to analyze soil health card. Please try again.');
      console.error('Soil analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCameraCapture = () => {
    // This would integrate with device camera
    // For now, just trigger file input
    fileInputRef.current?.click();
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  // Only show data if soil analysis is complete
  const cropData = soilData?.fertilizer_plan?.crop_data;
  const currentPlan = soilData?.fertilizer_plan?.current_plan;
  const soilHealth = soilData?.soil_health;
  const recommendations = soilData?.fertilizer_plan?.recommendations;

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
          {t('fertilizer.title')}
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

      {/* File Upload Section */}
      {!soilData && (
        <Card className="mb-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardHeader>
            <CardTitle className="text-lg text-blue-800 flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Upload Soil Health Card
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-blue-700 text-sm">
                Upload a photo of your soil health card to get personalized fertilizer recommendations.
              </p>
              
              {error && (
                <div className="p-3 bg-red-100 border border-red-300 rounded-lg">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}
              
              <div className="flex gap-3">
                <Button
                  onClick={triggerFileInput}
                  disabled={isLoading}
                  className="flex-1"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  {isLoading ? 'Analyzing...' : 'Upload Photo'}
                </Button>
                
                <Button
                  onClick={handleCameraCapture}
                  disabled={isLoading}
                  variant="outline"
                  className="flex-1"
                >
                  <Camera className="h-4 w-4 mr-2" />
                  Camera
                </Button>
              </div>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Crop Status Card */}
      {cropData && (
        <Card className="mb-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-green-800">
              <Leaf className="h-6 w-6" />
              Crop Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="font-bold text-lg text-green-800">
                  {cropData.name}
                </p>
                <p className="text-green-700">
                  {cropData.stage}
                </p>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Crop Progress</span>
                  <span>{cropData.progress}%</span>
                </div>
                <Progress value={cropData.progress} className="h-2" />
              </div>
              
              <div className="flex items-center gap-2 p-3 bg-green-200 rounded-lg">
                <Clock className="h-5 w-5 text-green-700" />
                <div>
                  <p className="text-sm font-medium text-green-800">
                    Next Fertilizer
                  </p>
                  <p className="text-xs text-green-700">
                    {cropData.nextFertilizer}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Fertilizer Plan */}
      {currentPlan && currentPlan.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Current Fertilizer Plan
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {currentPlan.map((item, index) => (
                <div 
                  key={index}
                  className={`p-4 rounded-lg border-2 ${
                    item.status === 'pending' 
                      ? 'bg-red-50 border-red-200' 
                      : item.status === 'upcoming'
                      ? 'bg-yellow-50 border-yellow-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-bold text-lg">
                        {item.fertilizer}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {item.amount}
                      </p>
                    </div>
                    <Badge 
                      variant={
                        item.priority === 'high' 
                          ? 'destructive' 
                          : item.priority === 'medium' 
                          ? 'default' 
                          : 'secondary'
                      }
                      className="text-xs"
                    >
                      {item.priority === 'high' ? 'High Priority' : 
                       item.priority === 'medium' ? 'Medium Priority' : 'Low Priority'}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      <span>{item.timing}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Droplets className="h-4 w-4" />
                      <span>{item.method}</span>
                    </div>
                  </div>
                  
                  {item.status === 'pending' && (
                    <div className="flex items-center gap-2 mt-3 p-2 bg-red-100 rounded">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                      <p className="text-xs text-red-800 font-medium">
                        Apply immediately
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Soil Health */}
      {soilHealth && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Soil Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(soilHealth).map(([nutrient, data]) => (
                <div key={nutrient} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="capitalize">
                      {nutrient === 'nitrogen' ? 'Nitrogen' :
                       nutrient === 'phosphorus' ? 'Phosphorus' :
                       nutrient === 'potassium' ? 'Potassium' : 'pH Level'}
                    </span>
                    <span className="font-medium">{(data as any).level}</span>
                  </div>
                  <Progress 
                    value={(data as any).percentage} 
                    className={`h-2 ${
                      (data as any).percentage < 40 ? '[&>div]:bg-red-500' :
                      (data as any).percentage < 70 ? '[&>div]:bg-yellow-500' :
                      '[&>div]:bg-green-500'
                    }`}
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {recommendations && (
        <Card className="mb-6 bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-lg text-blue-800 flex items-center gap-2">
              <Package className="h-5 w-5" />
              Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <p className="font-medium text-blue-800">
                {recommendations.english}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="space-y-3">
        <Button 
          className="w-full h-12 text-lg"
          onClick={handleVoiceOutput}
        >
          <Volume2 className="h-5 w-5 mr-2" />
          Listen to Plan
        </Button>
        
        {soilData && (
          <Button 
            variant="outline" 
            className="w-full h-12"
            onClick={() => {
              setSoilData(null);
              setError(null);
              if (fileInputRef.current) {
                fileInputRef.current.value = '';
              }
            }}
          >
            <Upload className="h-5 w-5 mr-2" />
            Upload New Card
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

export default FertilizerPlan;