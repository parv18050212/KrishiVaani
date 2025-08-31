import React, { useState, useEffect } from 'react';
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
import { speechService, SpeechRecognitionResult, RAGResponse } from '../services/speechService';
import RAGResponsePopup from './RAGResponsePopup';
import LanguageSelector from './LanguageSelector';
import { useTranslation } from '../hooks/useTranslation';

interface DashboardProps {
  onFeatureSelect: (feature: string) => void;
  onLanguageChange: (languageCode: string) => void;
  selectedLanguage: string;
}

const Dashboard: React.FC<DashboardProps> = ({ onFeatureSelect, onLanguageChange, selectedLanguage }) => {
  const [isOnline, setIsOnline] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [isLanguageSelectorOpen, setIsLanguageSelectorOpen] = useState(false);
  const { t } = useTranslation();
  
  // RAG Response states
  const [ragResponse, setRagResponse] = useState<RAGResponse | null>(null);
  const [isRagPopupOpen, setIsRagPopupOpen] = useState(false);
  const [isLoadingRag, setIsLoadingRag] = useState(false);
  const [ragError, setRagError] = useState<string | null>(null);
  const [currentQuery, setCurrentQuery] = useState('');

  const features = [
    {
      id: 'weather',
      title: t('weather.title'),
      icon: CloudRain,
      color: 'bg-blue-50 hover:bg-blue-100 border-blue-200',
      iconColor: 'text-blue-600'
    },
    {
      id: 'pest',
      title: t('pest.title'),
      icon: Bug,
      color: 'bg-red-50 hover:bg-red-100 border-red-200',
      iconColor: 'text-red-600'
    },
    {
      id: 'fertilizer',
      title: t('fertilizer.title'),
      icon: Package,
      color: 'bg-green-50 hover:bg-green-100 border-green-200',
      iconColor: 'text-green-600'
    },
    {
      id: 'market',
      title: t('market.title'),
      icon: IndianRupee,
      color: 'bg-yellow-50 hover:bg-yellow-100 border-yellow-200',
      iconColor: 'text-yellow-600'
    }
  ];

  // Handle speech recognition result
  const handleSpeechResult = async (result: SpeechRecognitionResult) => {
    console.log('Speech result:', result);
    setCurrentQuery(result.transcript);
    setIsLoadingRag(true);
    setRagError(null);
    setIsRagPopupOpen(true);

    try {
      const response = await speechService.sendToRAG(result.transcript);
      setRagResponse(response);
    } catch (error) {
      console.error('RAG API error:', error);
      setRagError(error instanceof Error ? error.message : 'Failed to get response');
    } finally {
      setIsLoadingRag(false);
    }
  };

  // Handle speech recognition error
  const handleSpeechError = (error: string) => {
    console.error('Speech recognition error:', error);
    setRagError(`Speech recognition error: ${error}`);
    setIsRagPopupOpen(true);
    setIsLoadingRag(false);
  };

  // Handle speech recognition end
  const handleSpeechEnd = () => {
    setIsListening(false);
  };

  const handleVoiceInput = () => {
    if (isListening) {
      speechService.stopListening();
    } else {
      // Set language before starting
      speechService.setLanguage(selectedLanguage);
      speechService.startListening(
        handleSpeechResult,
        handleSpeechError,
        handleSpeechEnd
      );
      setIsListening(true);
    }
  };

  // Update speech service language when selected language changes
  useEffect(() => {
    speechService.setLanguage(selectedLanguage);
  }, [selectedLanguage]);

  return (
    <div className="min-h-screen bg-background p-4 max-w-md mx-auto pb-20">
      {/* Header with offline indicator and language selector */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          {isOnline ? (
            <Wifi className="h-4 w-4 text-green-600" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-500" />
          )}
          <Badge variant={isOnline ? "secondary" : "destructive"} className="text-xs">
            {isOnline ? t('common.online') : t('common.offline')}
          </Badge>
        </div>
        
        <LanguageSelector
          selectedLanguage={selectedLanguage}
          onLanguageChange={onLanguageChange}
          isOpen={isLanguageSelectorOpen}
          onToggle={() => setIsLanguageSelectorOpen(!isLanguageSelectorOpen)}
        />
      </div>

      {/* App Title */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-primary mb-2">
          {t('dashboard.appTitle')}
        </h1>
        <p className="text-muted-foreground text-lg">
          {t('dashboard.subtitle')}
        </p>
      </div>

      {/* Voice Input Button */}
      <div className="flex justify-center mb-8">
        <div className="relative">
          <Button
            onClick={handleVoiceInput}
            size="lg"
            className={`h-20 w-20 rounded-full ${
              isListening 
                ? 'bg-red-500 hover:bg-red-600 shadow-red-500/50' 
                : 'bg-primary hover:bg-primary/90 shadow-primary/30'
            } transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105`}
          >
            <Mic className={`h-10 w-10 transition-all duration-300 ${
              isListening ? 'animate-pulse' : ''
            }`} />
          </Button>
          
          {/* Ripple effect when listening */}
          {isListening && (
            <>
              <div className="absolute inset-0 rounded-full bg-red-500/20 animate-ping"></div>
              <div className="absolute inset-0 rounded-full bg-red-500/10 animate-pulse"></div>
            </>
          )}
        </div>
      </div>

      {isListening && (
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-2">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <p className="text-red-600 font-medium text-lg">
              {t('dashboard.listening')}
            </p>
          </div>
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
          {t('dashboard.quickHelp')}
        </p>
      </div>

      {/* RAG Response Popup */}
      <RAGResponsePopup
        isOpen={isRagPopupOpen}
        onClose={() => setIsRagPopupOpen(false)}
        response={ragResponse}
        query={currentQuery}
        isLoading={isLoadingRag}
        error={ragError}
      />
    </div>
  );
};

export default Dashboard;