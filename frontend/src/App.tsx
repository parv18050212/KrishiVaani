import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import WeatherAdvisory from './components/WeatherAdvisory';
import PestDetection from './components/PestDetection';
import FertilizerPlan from './components/FertilizerPlan';
import MarketPrice from './components/MarketPrice';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<string>('dashboard');

  const handleFeatureSelect = (feature: string) => {
    setCurrentScreen(feature);
  };

  const handleBackToDashboard = () => {
    setCurrentScreen('dashboard');
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'weather':
        return <WeatherAdvisory onBack={handleBackToDashboard} />;
      case 'pest':
        return <PestDetection onBack={handleBackToDashboard} />;
      case 'fertilizer':
        return <FertilizerPlan onBack={handleBackToDashboard} />;
      case 'market':
        return <MarketPrice onBack={handleBackToDashboard} />;
      case 'dashboard':
      default:
        return <Dashboard onFeatureSelect={handleFeatureSelect} />;
    }
  };

  return (
    <div className="size-full">
      {renderScreen()}
    </div>
  );
}