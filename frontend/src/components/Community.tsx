import React from 'react';
import { Users, MessageCircle, Heart, Share2 } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';

interface CommunityProps {
  onBack: () => void;
  selectedLanguage: string;
}

const Community: React.FC<CommunityProps> = ({ onBack, selectedLanguage }) => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 pb-20">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="flex items-center justify-between px-4 py-3">
          <button
            onClick={onBack}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold text-gray-800">Community</h1>
          <div className="w-10"></div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-6">
        {/* Welcome Section */}
        <div className="bg-white rounded-xl p-6 mb-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">Farmer Community</h2>
              <p className="text-gray-600 text-sm">Connect with fellow farmers</p>
            </div>
          </div>
          <p className="text-gray-700 leading-relaxed">
            Join our growing community of farmers to share experiences, ask questions, and learn from each other. 
            This is a place where knowledge meets practice.
          </p>
        </div>

        {/* Community Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-gray-600">Members</span>
            </div>
            <p className="text-2xl font-bold text-gray-800">1,247</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <MessageCircle className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-gray-600">Discussions</span>
            </div>
            <p className="text-2xl font-bold text-gray-800">3,891</p>
          </div>
        </div>

        {/* Recent Discussions */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Discussions</h3>
          <div className="space-y-4">
            <div className="border-b border-gray-100 pb-4 last:border-b-0">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-green-600">RK</span>
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-800 mb-1">Best practices for organic farming</h4>
                  <p className="text-sm text-gray-600 mb-2">Looking for advice on transitioning to organic methods...</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>2 hours ago</span>
                    <div className="flex items-center gap-1">
                      <Heart className="w-3 h-3" />
                      <span>12</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle className="w-3 h-3" />
                      <span>8</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="border-b border-gray-100 pb-4 last:border-b-0">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-600">SM</span>
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-800 mb-1">Weather impact on wheat crop</h4>
                  <p className="text-sm text-gray-600 mb-2">How is everyone's wheat crop doing with the recent rains...</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>5 hours ago</span>
                    <div className="flex items-center gap-1">
                      <Heart className="w-3 h-3" />
                      <span>7</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle className="w-3 h-3" />
                      <span>15</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="border-b border-gray-100 pb-4 last:border-b-0">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-yellow-600">AP</span>
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-800 mb-1">New pest control methods</h4>
                  <p className="text-sm text-gray-600 mb-2">Has anyone tried the new biological pest control...</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>1 day ago</span>
                    <div className="flex items-center gap-1">
                      <Heart className="w-3 h-3" />
                      <span>23</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle className="w-3 h-3" />
                      <span>31</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Coming Soon Notice */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-6 text-white text-center">
          <Share2 className="w-8 h-8 mx-auto mb-3" />
          <h3 className="text-lg font-semibold mb-2">Full Community Features Coming Soon!</h3>
          <p className="text-green-100 text-sm">
            We're working on bringing you real-time chat, forums, and more interactive features.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Community;
