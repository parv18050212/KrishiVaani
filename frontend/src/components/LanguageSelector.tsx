import React, { useRef, useEffect, useState } from 'react';
import { ChevronDown, Globe } from 'lucide-react';
import { INDIAN_LANGUAGES } from '../services/speechService';
import { useTranslation } from '../hooks/useTranslation';

interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (languageCode: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  selectedLanguage,
  onLanguageChange,
  isOpen,
  onToggle
}) => {
  const selectedLang = INDIAN_LANGUAGES.find(lang => lang.code === selectedLanguage) || INDIAN_LANGUAGES[0];
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [dropdownPosition, setDropdownPosition] = useState<'bottom' | 'top'>('bottom');
  const { setLanguage } = useTranslation();

  // Calculate dropdown position to prevent overflow
  useEffect(() => {
    if (isOpen && dropdownRef.current) {
      const rect = dropdownRef.current.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      const dropdownHeight = Math.min(viewportHeight * 0.75, 400); // 3/4 of screen height, max 400px
      
      // Check if dropdown would overflow bottom
      if (rect.bottom + dropdownHeight > viewportHeight) {
        setDropdownPosition('top');
      } else {
        setDropdownPosition('bottom');
      }
    }
  }, [isOpen]);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={onToggle}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
      >
        <Globe size={16} className="text-gray-600" />
        <span className="text-gray-700">{selectedLang.nativeName}</span>
        <ChevronDown size={16} className={`text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div 
          className={`absolute left-0 right-0 bg-white border border-gray-300 rounded-lg shadow-xl z-50 ${
            dropdownPosition === 'bottom' 
              ? 'top-full mt-1' 
              : 'bottom-full mb-1'
          }`}
          style={{
            maxHeight: '75vh',
            minHeight: '200px',
            backgroundColor: 'white'
          }}
        >
          <div className="p-2 bg-white">
            <div className="text-xs font-medium text-gray-500 px-2 py-1 border-b border-gray-100 mb-1 sticky top-0 bg-white z-10">
              Select Language
            </div>
            <div className="overflow-y-auto overflow-x-hidden" style={{ maxHeight: 'calc(75vh - 60px)' }}>
              {INDIAN_LANGUAGES.map((language) => (
                <button
                  key={language.code}
                                  onClick={() => {
                  onLanguageChange(language.code);
                  setLanguage(language.code); // Update translation service
                  onToggle();
                }}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                    selectedLanguage === language.code
                      ? 'bg-green-100 text-green-700 font-medium'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{language.nativeName}</div>
                      <div className="text-xs text-gray-500">{language.name}</div>
                    </div>
                    {selectedLanguage === language.code && (
                      <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;

