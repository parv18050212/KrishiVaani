import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { 
  Mic, 
  Cloud, 
  Bug, 
  Package, 
  IndianRupee, 
  CloudRain, 
  Leaf, 
  Wifi,
  WifiOff,
  Globe
} from 'lucide-react';

interface DashboardProps {
  onFeatureSelect: (feature: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onFeatureSelect }) => {
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [isOnline, setIsOnline] = useState(true);
  const [isListening, setIsListening] = useState(false);

  const languages = [
    { value: 'hi', label: 'हिंदी' },
    { value: 'ta', label: 'தமిழ்' },
    { value: 'te', label: 'తెలుగు' },
    { value: 'bn', label: 'বাংলা' },
    { value: 'gu', label: 'ગુજરાતી' },
    { value: 'kn', label: 'ಕನ್ನಡ' },
    { value: 'ml', label: 'മലയാളം' },
    { value: 'mr', label: 'मराठी' },
    { value: 'pa', label: 'ਪੰਜਾਬੀ' },
    { value: 'en', label: 'English' }
  ];

  const features = [
    {
      id: 'weather',
      title: 'Weather Advisory',
      icon: CloudRain,
      color: 'bg-blue-50 hover:bg-blue-100 border-blue-200',
      iconColor: 'text-blue-600'
    },
    {
      id: 'pest',
      title: 'Pest Detection',
      icon: Bug,
      color: 'bg-red-50 hover:bg-red-100 border-red-200',
      iconColor: 'text-red-600'
    },
    {
      id: 'fertilizer',
      title: 'Fertilizer Plan',
      icon: Package,
      color: 'bg-green-50 hover:bg-green-100 border-green-200',
      iconColor: 'text-green-600'
    },
    {
      id: 'market',
      title: 'Market Price',
      icon: IndianRupee,
      color: 'bg-yellow-50 hover:bg-yellow-100 border-yellow-200',
      iconColor: 'text-yellow-600'
    }
  ];

  const handleVoiceInput = () => {
    setIsListening(!isListening);
    // Mock voice input functionality
    setTimeout(() => setIsListening(false), 3000);
  };

  return (
    <div className="min-h-screen bg-background p-4 max-w-md mx-auto">
      {/* Header with offline indicator and language selector */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          {isOnline ? (
            <Wifi className="h-4 w-4 text-green-600" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-500" />
          )}
          <Badge variant={isOnline ? "secondary" : "destructive"} className="text-xs">
            {isOnline ? 'Online' : 'Offline'}
          </Badge>
        </div>
        

      </div>

      {/* App Title */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-primary mb-2">
          Farmer Friend
        </h1>
        <p className="text-muted-foreground text-lg">
          AI Crop Advisory
        </p>
      </div>

      {/* Voice Input Button */}
      <div className="flex justify-center mb-8">
        <Button
          onClick={handleVoiceInput}
          size="lg"
          className={`h-20 w-20 rounded-full ${
            isListening ? 'bg-red-500 hover:bg-red-600 animate-pulse' : 'bg-primary hover:bg-primary/90'
          } transition-all duration-300 shadow-lg`}
        >
          <Mic className="h-10 w-10" />
        </Button>
      </div>

      {isListening && (
        <div className="text-center mb-6">
          <p className="text-primary font-medium text-lg animate-pulse">
            Listening...
          </p>
        </div>
      )}

      {/* Feature Cards Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {features.map((feature) => (
          <Card
            key={feature.id}
            className={`${feature.color} border-2 cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-lg`}
            onClick={() => onFeatureSelect(feature.id)}
          >
            <CardContent className="p-6 text-center">
              <feature.icon className={`h-12 w-12 mx-auto mb-3 ${feature.iconColor}`} />
              <h3 className="font-bold text-lg mb-1 leading-tight">
                {feature.title}
              </h3>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Help */}
      <div className="text-center">
        <p className="text-muted-foreground text-sm">
          Press mic button or select a card
        </p>
      </div>
    </div>
  );
};

export default Dashboard;