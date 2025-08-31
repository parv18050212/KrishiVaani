import React, { useEffect } from 'react';
import { X, Mic, Volume2, FileText, CheckCircle, AlertCircle, ChevronUp } from 'lucide-react';
import { RAGResponse } from '../services/speechService';

interface RAGResponsePopupProps {
  isOpen: boolean;
  onClose: () => void;
  response: RAGResponse | null;
  query: string;
  isLoading: boolean;
  error: string | null;
}

const RAGResponsePopup: React.FC<RAGResponsePopupProps> = ({
  isOpen,
  onClose,
  response,
  query,
  isLoading,
  error
}) => {
  // Prevent body scroll when popup is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'hi-IN'; // Default to Hindi
      utterance.rate = 0.9;
      utterance.pitch = 1;
      speechSynthesis.speak(utterance);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black z-40 animate-in fade-in duration-300"
        onClick={onClose}
      />

             {/* Bottom Sheet */}
       <div className="fixed bottom-0 left-0 right-0 z-50 animate-in slide-in-from-bottom duration-300 ease-out">
         <div className="bg-green-600 rounded-t-3xl shadow-2xl h-[75vh] overflow-hidden border-t-4 border-green-500">
           {/* Drag Handle */}
           <div className="flex justify-center pt-4 pb-2">
             <div className="w-12 h-1.5 bg-gray-300 rounded-full"></div>
           </div>

           {/* Header */}
           <div className="text-white px-6 py-4 relative">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                <h2 className="text-lg font-bold">KrishiVaani AI Assistant</h2>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:text-gray-200 transition-colors p-2 rounded-full hover:bg-white/10"
              >
                <X size={20} />
              </button>
            </div>
            
            {/* Query Display */}
            {query && (
              <div className="mt-3 bg-green-700 rounded-xl p-3">
                <div className="flex items-center gap-2 text-sm">
                  <Mic size={14} />
                  <span className="font-medium">Your Question:</span>
                </div>
                <p className="mt-1 text-white/90 text-sm leading-relaxed">{query}</p>
              </div>
            )}
          </div>

                     {/* Content */}
           <div className="px-6 py-4 overflow-y-auto max-h-[60vh] bg-white rounded-t-3xl">
            {isLoading && (
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <div className="w-12 h-12 border-3 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                  <p className="text-gray-700 font-medium text-sm">Processing your question...</p>
                  <p className="text-xs text-gray-500 mt-1">Searching knowledge base</p>
                </div>
              </div>
            )}

                         {error && (
               <div className="flex items-center gap-3 p-4 bg-white border border-red-200 rounded-xl">
                <AlertCircle className="text-red-500 flex-shrink-0" size={18} />
                <div>
                  <p className="text-red-700 font-medium text-sm">Error</p>
                  <p className="text-red-600 text-xs">{error}</p>
                </div>
              </div>
            )}

            {response && !isLoading && (
              <div className="space-y-4">
                                 {/* Main Answer */}
                 <div className="bg-white border border-green-200 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle className="text-green-600 flex-shrink-0" size={18} />
                    <h3 className="font-semibold text-green-800 text-sm">AI Response</h3>
                    <button
                      onClick={() => speakText(response.answer)}
                      className="ml-auto p-1.5 bg-green-100 hover:bg-green-200 rounded-full transition-colors"
                      title="Listen to response"
                    >
                      <Volume2 size={14} className="text-green-600" />
                    </button>
                  </div>
                  <p className="text-gray-800 leading-relaxed whitespace-pre-wrap text-sm">
                    {response.answer}
                  </p>
                </div>

                                 {/* Sources */}
                 {response.sources && response.sources.length > 0 && (
                   <div className="bg-white border border-blue-200 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <FileText className="text-blue-600 flex-shrink-0" size={18} />
                      <h3 className="font-semibold text-blue-800 text-sm">
                        Knowledge Sources ({response.sources.length})
                      </h3>
                    </div>
                    <div className="space-y-3">
                      {response.sources.slice(0, 3).map((source, index) => (
                        <div key={source.id} className="bg-white rounded-lg p-3 border border-blue-100">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                            <span className="text-xs font-medium text-blue-700">
                              Source {index + 1}
                            </span>
                            <span className="text-xs text-gray-500">
                              ({Math.round((1 - source.similarity_score) * 100)}% match)
                            </span>
                          </div>
                          <p className="text-xs text-gray-700 leading-relaxed">
                            {source.preview}
                          </p>
                          {source.metadata && (
                            <div className="mt-2 flex flex-wrap gap-1">
                              {Object.entries(source.metadata).slice(0, 2).map(([key, value]) => (
                                <span
                                  key={key}
                                  className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full"
                                >
                                  {key}: {String(value)}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                      {response.sources.length > 3 && (
                        <div className="text-center">
                          <span className="text-xs text-gray-500">
                            +{response.sources.length - 3} more sources
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Context Status */}
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <div className={`w-1.5 h-1.5 rounded-full ${response.has_context ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                  <span>
                    {response.has_context 
                      ? 'Response based on knowledge base' 
                      : 'Response from general knowledge'
                    }
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-3 border-t">
            <div className="flex items-center justify-between text-xs text-gray-600">
              <div className="flex items-center gap-3">
                <span>KrishiVaani AI</span>
                <span>•</span>
                <span>Agriculture Assistant</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default RAGResponsePopup;

