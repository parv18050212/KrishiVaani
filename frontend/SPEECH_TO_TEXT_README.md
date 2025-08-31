# Speech-to-Text Integration with RAG System

## Overview

This implementation adds speech-to-text functionality to the KrishiVaani frontend with support for 22 Indian languages and integration with the RAG (Retrieval-Augmented Generation) system.

## Features

### 🎤 Speech Recognition
- **22 Indian Languages Support**: Hindi, Bengali, Telugu, Tamil, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese, Nepali, Urdu, Sinhala, Burmese, Thai, Khmer, Lao, Vietnamese, Indonesian, Malay, and English
- **Real-time Speech Processing**: Uses Web Speech API for browser-based speech recognition
- **Language Switching**: Dynamic language selection without page reload

### 🤖 RAG Integration
- **Smart Context Retrieval**: Enhanced search with 6 context chunks for speech queries
- **Voice-Optimized Responses**: Concise, clear responses suitable for voice communication
- **Source Attribution**: Shows knowledge sources with confidence scores
- **F1-Style Popup**: Modern overlay display for responses

### 🎨 UI Components
- **Language Selector**: Dropdown with native language names
- **RAG Response Popup**: F1-style overlay with response details
- **Voice Button**: Animated microphone button with listening states
- **Text-to-Speech**: Built-in speech synthesis for responses

## Architecture

### Frontend Components

1. **SpeechService** (`src/services/speechService.ts`)
   - Manages Web Speech API integration
   - Handles language switching
   - Communicates with RAG backend

2. **LanguageSelector** (`src/components/LanguageSelector.tsx`)
   - Dropdown for 22 Indian languages
   - Native language display
   - Real-time language switching

3. **RAGResponsePopup** (`src/components/RAGResponsePopup.tsx`)
   - F1-style overlay design
   - Response display with sources
   - Text-to-speech functionality

4. **Dashboard** (`src/components/Dashboard.tsx`)
   - Integrated speech button
   - State management for speech recognition
   - RAG response handling

### Backend Endpoints

1. **`/chat/speech`** (New)
   - Specialized endpoint for speech queries
   - Enhanced context retrieval (6 chunks)
   - Voice-optimized response generation
   - Shorter, clearer responses

## Usage

### For Users

1. **Select Language**: Click the language selector in the top-right corner
2. **Start Speaking**: Click the microphone button in the center
3. **Ask Question**: Speak your agricultural question in the selected language
4. **View Response**: See the AI response in the F1-style popup
5. **Listen to Response**: Click the speaker icon to hear the response

### For Developers

#### Adding New Languages

1. Update `INDIAN_LANGUAGES` array in `speechService.ts`:
```typescript
{ code: 'xx-IN', name: 'Language Name (English)', nativeName: 'Native Name' }
```

2. Ensure the language code follows the format: `language-COUNTRY`

#### Customizing Speech Recognition

```typescript
// Set language
speechService.setLanguage('hi-IN');

// Start listening
speechService.startListening(
  (result) => console.log('Transcript:', result.transcript),
  (error) => console.error('Error:', error),
  () => console.log('Recognition ended')
);
```

#### Modifying RAG Response Display

Edit `RAGResponsePopup.tsx` to customize:
- Popup styling
- Response format
- Source display
- Text-to-speech behavior

## Technical Details

### Speech Recognition Flow

1. User clicks microphone button
2. `speechService.setLanguage()` sets recognition language
3. `speechService.startListening()` begins recognition
4. Web Speech API processes audio
5. `onresult` callback receives transcript
6. Transcript sent to `/chat/speech` endpoint
7. RAG system processes query with enhanced context
8. Response displayed in F1-style popup

### Language Support Matrix

| Language | Code | Native Name | Status |
|----------|------|-------------|--------|
| Hindi | hi-IN | हिंदी | ✅ |
| Bengali | bn-IN | বাংলা | ✅ |
| Telugu | te-IN | తెలుగు | ✅ |
| Tamil | ta-IN | தமிழ் | ✅ |
| Marathi | mr-IN | मराठी | ✅ |
| Gujarati | gu-IN | ગુજરાતી | ✅ |
| Kannada | kn-IN | ಕನ್ನಡ | ✅ |
| Malayalam | ml-IN | മലയാളം | ✅ |
| Punjabi | pa-IN | ਪੰਜਾਬੀ | ✅ |
| Odia | or-IN | ଓଡ଼ିଆ | ✅ |
| Assamese | as-IN | অসমীয়া | ✅ |
| Nepali | ne-IN | नेपाली | ✅ |
| Urdu | ur-IN | اردو | ✅ |
| Sinhala | si-IN | සිංහල | ✅ |
| Burmese | my-IN | မြန်မာ | ✅ |
| Thai | th-IN | ไทย | ✅ |
| Khmer | km-IN | ខ្មែរ | ✅ |
| Lao | lo-IN | ລາວ | ✅ |
| Vietnamese | vi-IN | Tiếng Việt | ✅ |
| Indonesian | id-IN | Bahasa Indonesia | ✅ |
| Malay | ms-IN | Bahasa Melayu | ✅ |
| English | en-IN | English | ✅ |

### Browser Compatibility

- **Chrome**: Full support
- **Edge**: Full support
- **Safari**: Limited support (webkitSpeechRecognition)
- **Firefox**: Limited support
- **Mobile Browsers**: Varies by platform

## Error Handling

### Speech Recognition Errors

- **Not Supported**: Fallback to text input
- **Permission Denied**: User guidance for microphone access
- **Network Error**: Retry mechanism
- **No Speech Detected**: Timeout handling

### RAG API Errors

- **Connection Failed**: Offline mode indication
- **Invalid Response**: Error display in popup
- **Timeout**: Retry with shorter context

## Performance Optimizations

1. **Context Limiting**: 1200 characters per context block
2. **Response Length**: 600 tokens max for voice responses
3. **Language Caching**: Prevents unnecessary API calls
4. **Debounced Recognition**: Prevents multiple simultaneous requests

## Security Considerations

1. **HTTPS Required**: Speech API requires secure connection
2. **Permission Handling**: Explicit microphone permission requests
3. **Data Privacy**: No audio storage, only transcript processing
4. **API Rate Limiting**: Built-in request throttling

## Future Enhancements

1. **Offline Speech Recognition**: Local processing capabilities
2. **Voice Commands**: Navigation and control via voice
3. **Multi-language Support**: Automatic language detection
4. **Voice Profiles**: Personalized speech recognition
5. **Advanced TTS**: Natural-sounding voice synthesis

