import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  ArrowLeft, 
  Volume2, 
  Camera, 
  Upload, 
  Bug, 
  Leaf,
  AlertTriangle,
  CheckCircle,
  Eye,
  Loader2
} from 'lucide-react';
import { pestDetectionAPI, PestDetectionResult } from '../services/api';
import { useTranslation } from '../hooks/useTranslation';

interface PestDetectionProps {
  onBack: () => void;
  selectedLanguage: string;
}

const PestDetection: React.FC<PestDetectionProps> = ({ onBack, selectedLanguage }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasImage, setHasImage] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<PestDetectionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { t } = useTranslation();

  const handleVoiceOutput = () => {
    setIsPlaying(!isPlaying);
    setTimeout(() => setIsPlaying(false), 5000);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
        setHasImage(true);
        setError(null);
        analyzeImage(file);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCameraClick = () => {
    fileInputRef.current?.click();
  };

  const handleGalleryClick = () => {
    fileInputRef.current?.click();
  };

  const analyzeImage = async (file: File) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Sending image to API...');
      const result = await pestDetectionAPI.detectPest(file);
      console.log('API Response:', result);
      setAnalysisResult(result);
    } catch (err: any) {
      console.error('Error analyzing image:', err);
      console.error('Error response:', err.response);
      console.error('Error data:', err.response?.data);
      setError(err.response?.data?.detail || t('error.analyzingImage'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-4 max-w-md mx-auto pb-20">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="ghost"
          size="lg"
          onClick={onBack}
          className="p-2"
        >
          <ArrowLeft className="h-6 w-6" />
        </Button>
        
        <h1 className="text-xl font-bold text-primary">
          {t('pest.title')}
        </h1>
        
        <Button
          onClick={handleVoiceOutput}
          size="lg"
          variant="outline"
          className={`p-2 ${isPlaying ? 'bg-primary text-primary-foreground animate-pulse' : ''}`}
        >
          <Volume2 className="h-6 w-6" />
        </Button>
      </div>

      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept="image/*"
        style={{ display: 'none' }}
      />

      {/* Error Message */}
      {error && (
        <Card className="mb-6 bg-red-50 border-red-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-red-800">
              <AlertTriangle className="h-5 w-5" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Image Upload Section */}
      {!hasImage ? (
        <Card className="mb-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="p-8 text-center">
            <div className="mb-6">
              <div className="mx-auto w-20 h-20 bg-green-200 rounded-full flex items-center justify-center mb-4">
                <Camera className="h-10 w-10 text-green-600" />
              </div>
              <h3 className="text-lg font-bold text-green-800 mb-2">
                {t('pest.takePhoto')}
              </h3>
              <p className="text-green-700 mb-4">
                {t('pest.uploadImage')}
              </p>
            </div>
            
            <div className="space-y-3">
              <Button 
                onClick={handleCameraClick}
                className="w-full h-12 text-lg bg-green-600 hover:bg-green-700"
              >
                <Camera className="h-5 w-5 mr-2" />
                {t('pest.takePhoto')}
              </Button>
              
              <Button 
                onClick={handleGalleryClick}
                variant="outline" 
                className="w-full h-12 text-lg border-green-300"
              >
                <Upload className="h-5 w-5 mr-2" />
                {t('pest.chooseFromGallery')}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="mb-6">
          <CardContent className="p-4">
            {selectedImage && (
              <div className="mb-4">
                <img 
                  src={selectedImage} 
                  alt="Selected crop" 
                  className="w-full h-48 object-cover rounded-lg"
                />
              </div>
            )}
            
            {isLoading && (
              <div className="text-center py-8">
                <Loader2 className="h-12 w-12 mx-auto text-green-600 mb-4 animate-spin" />
                <p className="text-sm text-muted-foreground">
                  {t('pest.analyzing')}
                </p>
                <div className="mt-4 space-y-2">
                  <div className="animate-pulse">
                    <div className="h-2 bg-green-200 rounded mb-2"></div>
                    <div className="h-2 bg-green-200 rounded w-3/4 mx-auto"></div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {analysisResult && (
        <>
          {/* Pest Detection Info Card */}
          <Card className="mb-6 bg-gradient-to-br from-red-50 to-red-100 border-red-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bug className="h-5 w-5 text-red-600" />
                  <div>
                    <p className="font-bold text-red-800">{analysisResult.pest_detection.pest_name}</p>
                    <p className="text-sm text-red-700">{t('pest.confidence')}: {analysisResult.pest_detection.confidence}</p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge className="bg-red-100 text-red-800 border-red-300">
                    {analysisResult.pest_detection.severity}
                  </Badge>
                  <p className="text-xs text-red-700 mt-1">
                    AI Model: {analysisResult.analysis.ai_model_used}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Confidence Analysis */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                {t('pest.detectionResult')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Overall Confidence */}
                <div className="flex items-center justify-between p-4 rounded-lg border border-muted">
                  <div>
                    <p className="font-bold text-lg">{t('pest.confidence')}</p>
                    <p className="text-sm text-muted-foreground">AI Analysis Score</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-xl text-blue-600">
                      {analysisResult.pest_detection.confidence_score}%
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {analysisResult.pest_detection.confidence}
                    </p>
                  </div>
                </div>

                {/* Confidence Breakdown */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Image Quality:</span>
                    <span className="text-sm font-medium">{analysisResult.pest_detection.confidence_breakdown.image_quality}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Pest Match:</span>
                    <span className="text-sm font-medium">{analysisResult.pest_detection.confidence_breakdown.pest_name_match}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Pesticide Data:</span>
                    <span className="text-sm font-medium">{analysisResult.pest_detection.confidence_breakdown.pesticide_availability}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Response Quality:</span>
                    <span className="text-sm font-medium">{analysisResult.pest_detection.confidence_breakdown.response_consistency}</span>
                  </div>
                </div>

                {/* Quality Indicators */}
                <div className="flex flex-wrap gap-2 pt-3 border-t border-muted">
                  {analysisResult.pest_detection.confidence_factors.image_size_adequate && (
                    <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                      ✓ Good Image
                    </Badge>
                  )}
                  {analysisResult.pest_detection.confidence_factors.pest_in_database && (
                    <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                      ✓ Known Pest
                    </Badge>
                  )}
                  {analysisResult.pest_detection.confidence_factors.pesticides_available && (
                    <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                      ✓ Treatment Available
                    </Badge>
                  )}
                  {analysisResult.pest_detection.confidence_factors.response_consistent && (
                    <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                      ✓ Reliable Analysis
                    </Badge>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Severity Alert */}
          {analysisResult.pest_detection.severity === 'High' && (
            <Card className="mb-6 bg-red-50 border-red-200">
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <p className="text-sm text-red-800 font-medium">
                    Immediate treatment needed - High severity pest detected
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
          {analysisResult.pest_detection.severity === 'Medium' && (
            <Card className="mb-6 bg-yellow-50 border-yellow-200">
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  <p className="text-sm text-yellow-800 font-medium">
                    Treatment recommended - Monitor closely
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
          {analysisResult.pest_detection.severity === 'Low' && (
            <Card className="mb-6 bg-green-50 border-green-200">
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <p className="text-sm text-green-800 font-medium">
                    Minimal threat - Continue monitoring
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Treatment Recommendations */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                {t('pest.treatment')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 rounded-lg border border-muted">
                  <p className="font-medium text-blue-800">
                    {analysisResult.treatment.recommendations.english}
                  </p>
                </div>
                
                {analysisResult.treatment.pesticides && analysisResult.treatment.pesticides.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-blue-800 mb-2">
                      Recommended Pesticides:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.treatment.pesticides.map((pesticide, index) => (
                        <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800">
                          {pesticide}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Prevention Tips */}
          <Card className="mb-6 bg-green-50 border-green-200">
            <CardHeader>
              <CardTitle className="text-lg text-green-800 flex items-center gap-2">
                <Leaf className="h-5 w-5" />
                {t('pest.prevention')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="font-medium text-green-800">
                  {analysisResult.treatment.prevention.english}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Info */}
          <Card className="mb-6 bg-gray-50 border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg text-gray-800 flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Analysis Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Processing Time:</span>
                  <span className="text-sm font-medium">{analysisResult.analysis.processing_time}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">AI Model:</span>
                  <span className="text-sm font-medium">{analysisResult.analysis.ai_model_used}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Image Processed:</span>
                  <span className="text-sm font-medium">{analysisResult.analysis.image_processed ? 'Yes' : 'No'}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Action Buttons */}
      <div className="space-y-3">
        {analysisResult && (
          <Button 
            className="w-full h-12 text-lg"
            onClick={handleVoiceOutput}
          >
            <Volume2 className="h-5 w-5 mr-2" />
            Listen to Treatment
          </Button>
        )}
        
        {hasImage && (
          <Button 
            variant="outline" 
            className="w-full h-12"
            onClick={() => {
              setHasImage(false);
              setAnalysisResult(null);
              setSelectedImage(null);
              setError(null);
              if (fileInputRef.current) {
                fileInputRef.current.value = '';
              }
            }}
          >
            <Camera className="h-5 w-5 mr-2" />
            Take New Photo
          </Button>
        )}
        
        <Button 
          variant="outline" 
          className="w-full h-12"
          onClick={onBack}
        >
          Go Back
        </Button>
      </div>
    </div>
  );
};

export default PestDetection;