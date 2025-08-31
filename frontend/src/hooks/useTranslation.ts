import { useState, useEffect } from 'react';
import { translationService } from '../services/translationService';

export const useTranslation = () => {
  const [, forceUpdate] = useState({});

  useEffect(() => {
    // Force re-render when language changes
    const handleLanguageChange = () => {
      forceUpdate({});
    };

    // Listen for language changes (you can implement a custom event system)
    window.addEventListener('languageChange', handleLanguageChange);
    
    return () => {
      window.removeEventListener('languageChange', handleLanguageChange);
    };
  }, []);

  const t = (key: string): string => {
    return translationService.translate(key);
  };

  const setLanguage = (languageCode: string) => {
    translationService.setLanguage(languageCode);
    // Dispatch custom event to notify components
    window.dispatchEvent(new CustomEvent('languageChange'));
  };

  const getCurrentLanguage = (): string => {
    return translationService.getLanguage();
  };

  return {
    t,
    setLanguage,
    getCurrentLanguage,
    currentLanguage: getCurrentLanguage()
  };
};
