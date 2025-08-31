export interface SpeechRecognitionResult {
  transcript: string;
  confidence: number;
  language: string;
}

export interface RAGResponse {
  answer: string;
  sources: Array<{
    id: string;
    metadata: any;
    similarity_score: number;
    preview: string;
  }>;
  has_context: boolean;
}

// Supported Indian languages with their codes
export const INDIAN_LANGUAGES = [
  { code: 'hi-IN', name: 'हिंदी (Hindi)', nativeName: 'हिंदी' },
  { code: 'bn-IN', name: 'বাংলা (Bengali)', nativeName: 'বাংলা' },
  { code: 'te-IN', name: 'తెలుగు (Telugu)', nativeName: 'తెలుగు' },
  { code: 'ta-IN', name: 'தமிழ் (Tamil)', nativeName: 'தமிழ்' },
  { code: 'mr-IN', name: 'मराठी (Marathi)', nativeName: 'मराठी' },
  { code: 'gu-IN', name: 'ગુજરાતી (Gujarati)', nativeName: 'ગુજરાતી' },
  { code: 'kn-IN', name: 'ಕನ್ನಡ (Kannada)', nativeName: 'ಕನ್ನಡ' },
  { code: 'ml-IN', name: 'മലയാളം (Malayalam)', nativeName: 'മലയാളം' },
  { code: 'pa-IN', name: 'ਪੰਜਾਬੀ (Punjabi)', nativeName: 'ਪੰਜਾਬੀ' },
  { code: 'or-IN', name: 'ଓଡ଼ିଆ (Odia)', nativeName: 'ଓଡ଼ିଆ' },
  { code: 'as-IN', name: 'অসমীয়া (Assamese)', nativeName: 'অসমীয়া' },
  { code: 'ne-IN', name: 'नेपाली (Nepali)', nativeName: 'नेपाली' },
  { code: 'ur-IN', name: 'اردو (Urdu)', nativeName: 'اردو' },
  { code: 'si-IN', name: 'සිංහල (Sinhala)', nativeName: 'සිංහල' },
  { code: 'my-IN', name: 'မြန်မာ (Burmese)', nativeName: 'မြန်မာ' },
  { code: 'th-IN', name: 'ไทย (Thai)', nativeName: 'ไทย' },
  { code: 'km-IN', name: 'ខ្មែរ (Khmer)', nativeName: 'ខ្មែរ' },
  { code: 'lo-IN', name: 'ລາວ (Lao)', nativeName: 'ລາວ' },
  { code: 'vi-IN', name: 'Tiếng Việt (Vietnamese)', nativeName: 'Tiếng Việt' },
  { code: 'id-IN', name: 'Bahasa Indonesia (Indonesian)', nativeName: 'Bahasa Indonesia' },
  { code: 'ms-IN', name: 'Bahasa Melayu (Malay)', nativeName: 'Bahasa Melayu' },
  { code: 'en-IN', name: 'English (Indian)', nativeName: 'English' }
];

class SpeechService {
  private recognition: any = null;
  private isListening = false;
  private onResultCallback: ((result: SpeechRecognitionResult) => void) | null = null;
  private onErrorCallback: ((error: string) => void) | null = null;
  private onEndCallback: (() => void) | null = null;

  constructor() {
    this.initializeSpeechRecognition();
  }

  private initializeSpeechRecognition() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.error('Speech recognition not supported');
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
    this.recognition.lang = 'hi-IN'; // Default to Hindi

    this.recognition.onresult = (event: any) => {
      const result = event.results[0];
      if (result.isFinal) {
        const transcript = result[0].transcript;
        const confidence = result[0].confidence;
        
        if (this.onResultCallback) {
          this.onResultCallback({
            transcript,
            confidence,
            language: this.recognition?.lang || 'hi-IN'
          });
        }
      }
    };

    this.recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      if (this.onErrorCallback) {
        this.onErrorCallback(event.error);
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (this.onEndCallback) {
        this.onEndCallback();
      }
    };
  }

  public setLanguage(languageCode: string) {
    if (this.recognition) {
      this.recognition.lang = languageCode;
    }
  }

  public startListening(
    onResult: (result: SpeechRecognitionResult) => void,
    onError: (error: string) => void,
    onEnd: () => void
  ) {
    if (!this.recognition) {
      onError('Speech recognition not supported');
      return;
    }

    this.onResultCallback = onResult;
    this.onErrorCallback = onError;
    this.onEndCallback = onEnd;

    try {
      this.recognition.start();
      this.isListening = true;
    } catch (error) {
      onError('Failed to start speech recognition');
    }
  }

  public stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }

  public isCurrentlyListening(): boolean {
    return this.isListening;
  }

  public async sendToRAG(query: string): Promise<RAGResponse> {
    try {
      const response = await fetch('http://43.204.140.241:8080/chat/speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          use_context: true,
          top_k: 6
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending query to RAG:', error);
      throw error;
    }
  }
}

export const speechService = new SpeechService();
