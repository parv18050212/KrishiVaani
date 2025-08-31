import React from 'react';
import { Home, Users, User } from 'lucide-react';

interface BottomNavigationProps {
  currentScreen: string;
  onNavigate: (screen: string) => void;
}

const BottomNavigation: React.FC<BottomNavigationProps> = ({ currentScreen, onNavigate }) => {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-green-600 border-t border-green-700 z-30">
      <div className="flex items-center justify-between py-1 px-4">
        {/* Home Button */}
        <button
          onClick={() => onNavigate('dashboard')}
          className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg transition-colors flex-1 ${
            currentScreen === 'dashboard' || currentScreen === 'weather' || currentScreen === 'pest' || currentScreen === 'fertilizer' || currentScreen === 'market'
              ? 'text-white bg-green-700'
              : 'text-green-100 hover:text-white hover:bg-green-700'
          }`}
        >
          <Home className="w-5 h-5 mb-0.5" />
          <span className="text-xs font-medium">Home</span>
        </button>

        {/* Community Button */}
        <button
          onClick={() => onNavigate('community')}
          className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg transition-colors flex-1 mx-2 ${
            currentScreen === 'community'
              ? 'text-white bg-green-700'
              : 'text-green-100 hover:text-white hover:bg-green-700'
          }`}
        >
          <Users className="w-5 h-5 mb-0.5" />
          <span className="text-xs font-medium">Community</span>
        </button>

        {/* Account Button */}
        <button
          onClick={() => onNavigate('account')}
          className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg transition-colors flex-1 ${
            currentScreen === 'account'
              ? 'text-white bg-green-700'
              : 'text-green-100 hover:text-white hover:bg-green-700'
          }`}
        >
          <User className="w-5 h-5 mb-0.5" />
          <span className="text-xs font-medium">Account</span>
        </button>
      </div>
    </div>
  );
};

export default BottomNavigation;
