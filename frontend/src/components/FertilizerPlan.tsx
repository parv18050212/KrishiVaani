import React, { useState } from 'react';
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
  AlertCircle
} from 'lucide-react';

interface FertilizerPlanProps {
  onBack: () => void;
}

const FertilizerPlan: React.FC<FertilizerPlanProps> = ({ onBack }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedCrop, setSelectedCrop] = useState('wheat');

  const handleVoiceOutput = () => {
    setIsPlaying(!isPlaying);
    setTimeout(() => setIsPlaying(false), 5000);
  };

  const cropData = {
    wheat: {
      name: 'Wheat',
      stage: 'Flowering Stage',
      progress: 65,
      nextFertilizer: 'In 15 days'
    }
  };

  const currentPlan = [
    {
      fertilizer: 'Urea',
      amount: '50 kg/acre',
      timing: 'Now',
      method: 'Broadcasting',
      status: 'pending',
      priority: 'high'
    },
    {
      fertilizer: 'DAP',
      amount: '25 kg/acre',
      timing: 'In 7 days',
      method: 'Mix in soil',
      status: 'upcoming',
      priority: 'medium'
    },
    {
      fertilizer: 'Potash',
      amount: '20 kg/acre',
      timing: 'In 20 days',
      method: 'Broadcasting',
      status: 'future',
      priority: 'low'
    }
  ];

  const soilHealth = {
    nitrogen: { level: 'Low', percentage: 30 },
    phosphorus: { level: 'Medium', percentage: 60 },
    potassium: { level: 'Good', percentage: 80 },
    ph: { level: '6.8 (Good)', percentage: 75 }
  };

  const recommendations = {
    english: 'Soil is low in nitrogen. Apply urea immediately. Apply fertilizer after irrigation.'
  };

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
          Fertilizer Plan
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

      {/* Crop Status Card */}
      <Card className="mb-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-green-800">
            <Leaf className="h-6 w-6" />
            फसल की स्थिति
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="font-bold text-lg text-green-800">
                {cropData.wheat.name}
              </p>
              <p className="text-green-700">
                {cropData.wheat.stage}
              </p>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>फसल की प्रगति / Crop Progress</span>
                <span>{cropData.wheat.progress}%</span>
              </div>
              <Progress value={cropData.wheat.progress} className="h-2" />
            </div>
            
            <div className="flex items-center gap-2 p-3 bg-green-200 rounded-lg">
              <Clock className="h-5 w-5 text-green-700" />
              <div>
                <p className="text-sm font-medium text-green-800">
                  अगली खाद
                </p>
                <p className="text-xs text-green-700">
                  {cropData.wheat.nextFertilizer}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Fertilizer Plan */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            वर्तमान खाद योजना
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
                    {item.priority === 'high' ? 'जरुरी' : 
                     item.priority === 'medium' ? 'मध्यम' : 'बाद में'}
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
                      तुरंत प्रयोग करें / Apply immediately
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Soil Health */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            मिट्टी का स्वास्थ्य
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(soilHealth).map(([nutrient, data]) => (
              <div key={nutrient} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="capitalize">
                    {nutrient === 'nitrogen' ? 'नाइट्रोजन' :
                     nutrient === 'phosphorus' ? 'फास्फोरस' :
                     nutrient === 'potassium' ? 'पोटेशियम' : 'pH स्तर'}
                  </span>
                  <span className="font-medium">{data.level}</span>
                </div>
                <Progress 
                  value={data.percentage} 
                  className={`h-2 ${
                    data.percentage < 40 ? '[&>div]:bg-red-500' :
                    data.percentage < 70 ? '[&>div]:bg-yellow-500' :
                    '[&>div]:bg-green-500'
                  }`}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card className="mb-6 bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-lg text-blue-800 flex items-center gap-2">
            <Package className="h-5 w-5" />
            सिफारिश / Recommendation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="font-medium text-blue-800">
              {recommendations.hindi}
            </p>
            <p className="text-sm text-blue-700">
              {recommendations.english}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="space-y-3">
        <Button 
          className="w-full h-12 text-lg"
          onClick={handleVoiceOutput}
        >
          <Volume2 className="h-5 w-5 mr-2" />
          योजना सुनें / Listen to Plan
        </Button>
        
        <Button 
          variant="outline" 
          className="w-full h-12"
          onClick={onBack}
        >
          वापस जाएं / Go Back
        </Button>
      </div>
    </div>
  );
};

export default FertilizerPlan;