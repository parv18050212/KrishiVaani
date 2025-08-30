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

interface PestDetectionProps {
  onBack: () => void;
}

const PestDetection: React.FC<PestDetectionProps> = ({ onBack }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasImage, setHasImage] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<PestDetectionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
      setError(err.response?.data?.detail || 'Error analyzing image. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-4 max-w-md mx-auto">
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
          Pest Detection
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
                Take Photo of Leaf or Crop
              </h3>
              <p className="text-green-700 mb-4">
                Upload an image to detect pests
              </p>
            </div>
            
            <div className="space-y-3">
              <Button 
                onClick={handleCameraClick}
                className="w-full h-12 text-lg bg-green-600 hover:bg-green-700"
              >
                <Camera className="h-5 w-5 mr-2" />
                Open Camera
              </Button>
              
              <Button 
                onClick={handleGalleryClick}
                variant="outline" 
                className="w-full h-12 text-lg border-green-300"
              >
                <Upload className="h-5 w-5 mr-2" />
                Choose from Gallery
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
                  Analyzing...
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
          <Card className="mb-6 bg-red-50 border-red-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-800">
                <Bug className="h-6 w-6" />
                Pest Identification
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold text-lg text-red-800">
                      {analysisResult.pestName}
                    </p>
                    <p className="text-sm text-red-600">
                      Confidence: {analysisResult.confidence}
                    </p>
                  </div>
                  <Badge 
                    variant="destructive" 
                    className="px-3 py-1"
                  >
                    {analysisResult.severity}
                  </Badge>
                </div>
                
                {/* Confidence Breakdown */}
                {analysisResult.confidenceBreakdown && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      Confidence Breakdown:
                    </p>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-600">Image Quality:</span>
                        <span className="text-xs font-medium">{analysisResult.confidenceBreakdown.image_quality}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-600">Pest Match:</span>
                        <span className="text-xs font-medium">{analysisResult.confidenceBreakdown.pest_name_match}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-600">Pesticide Data:</span>
                        <span className="text-xs font-medium">{analysisResult.confidenceBreakdown.pesticide_availability}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-600">Response Quality:</span>
                        <span className="text-xs font-medium">{analysisResult.confidenceBreakdown.response_consistency}</span>
                      </div>
                    </div>
                    
                    {/* Confidence Factors */}
                    {analysisResult.confidenceFactors && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-medium text-gray-700 mb-2">
                          Quality Indicators:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {analysisResult.confidenceFactors.image_size_adequate && (
                            <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                              ✓ Good Image
                            </Badge>
                          )}
                          {analysisResult.confidenceFactors.pest_in_database && (
                            <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                              ✓ Known Pest
                            </Badge>
                          )}
                          {analysisResult.confidenceFactors.pesticides_available && (
                            <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                              ✓ Treatment Available
                            </Badge>
                          )}
                          {analysisResult.confidenceFactors.response_consistent && (
                            <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                              ✓ Reliable Analysis
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                {analysisResult.severity === 'High' && (
                  <div className="flex items-center gap-2 p-3 bg-red-100 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-red-600" />
                    <p className="text-sm text-red-800 font-medium">
                      Immediate treatment needed
                    </p>
                  </div>
                )}
                {analysisResult.severity === 'Medium' && (
                  <div className="flex items-center gap-2 p-3 bg-yellow-100 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-yellow-600" />
                    <p className="text-sm text-yellow-800 font-medium">
                      Treatment recommended
                    </p>
                  </div>
                )}
                {analysisResult.severity === 'Low' && (
                  <div className="flex items-center gap-2 p-3 bg-green-100 rounded-lg">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <p className="text-sm text-green-800 font-medium">
                      Minimal threat - monitor closely
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Treatment Card */}
          <Card className="mb-6 bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-lg text-blue-800 flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Treatment
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="font-medium text-blue-800">
                  {analysisResult.treatment.english}
                </p>
                
                {analysisResult.pesticides && analysisResult.pesticides.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-blue-800 mb-2">
                      Recommended Pesticides:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.pesticides.map((pesticide, index) => (
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

          {/* Prevention Card */}
          <Card className="mb-6 bg-green-50 border-green-200">
            <CardHeader>
              <CardTitle className="text-lg text-green-800 flex items-center gap-2">
                <Leaf className="h-5 w-5" />
                Prevention
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="font-medium text-green-800">
                  {analysisResult.prevention.english}
                </p>
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