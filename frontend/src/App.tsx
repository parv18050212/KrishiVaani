import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import WeatherAdvisory from './components/WeatherAdvisory';
import PestDetection from './components/PestDetection';
import FertilizerPlan from './components/FertilizerPlan';
import MarketPrice from './components/MarketPrice';
import Community from './components/Community';
import Account from './components/Account';
import BottomNavigation from './components/BottomNavigation';
import { useTranslation } from './hooks/useTranslation';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<string>('dashboard');
  const { setLanguage, getCurrentLanguage } = useTranslation();
  const [selectedLanguage, setSelectedLanguage] = useState(getCurrentLanguage());

  const handleFeatureSelect = (feature: string) => {
    setCurrentScreen(feature);
  };

  const handleBackToDashboard = () => {
    setCurrentScreen('dashboard');
  };

  const handleLanguageChange = (languageCode: string) => {
    setSelectedLanguage(languageCode);
    setLanguage(languageCode);
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'weather':
        return <WeatherAdvisory onBack={handleBackToDashboard} selectedLanguage={selectedLanguage} />;
      case 'pest':
        return <PestDetection onBack={handleBackToDashboard} selectedLanguage={selectedLanguage} />;
      case 'fertilizer':
        return <FertilizerPlan onBack={handleBackToDashboard} selectedLanguage={selectedLanguage} />;
      case 'market':
        return <MarketPrice onBack={handleBackToDashboard} selectedLanguage={selectedLanguage} />;
      case 'community':
        return <Community onBack={handleBackToDashboard} selectedLanguage={selectedLanguage} />;
      case 'account':
        return <Account onBack={handleBackToDashboard} selectedLanguage={selectedLanguage} />;
      case 'dashboard':
      default:
        return <Dashboard onFeatureSelect={handleFeatureSelect} onLanguageChange={handleLanguageChange} selectedLanguage={selectedLanguage} />;
    }
  };

  return (
    <div className="size-full">
      {renderScreen()}
      <BottomNavigation currentScreen={currentScreen} onNavigate={setCurrentScreen} />
    </div>
  );
}