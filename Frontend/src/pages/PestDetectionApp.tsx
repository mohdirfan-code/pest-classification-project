import React, { useState } from 'react';
import { ImageUpload } from '@/components/ImageUpload';
import { LoadingState } from '@/components/LoadingState';
import { ResultsDisplay } from '@/components/ResultsDisplay';
import { PestApiService, PredictionResponse, RecommendationResponse } from '@/services/pestApi';
import { toast } from '@/hooks/use-toast';
import agriculturalHero from '@/assets/agricultural-hero.jpg';

type AppState = 'upload' | 'loading' | 'results';
type LoadingStage = 'predicting' | 'analyzing' | 'recommending';

export const PestDetectionApp: React.FC = () => {
  const [appState, setAppState] = useState<AppState>('upload');
  const [loadingStage, setLoadingStage] = useState<LoadingStage>('predicting');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string>('');
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);

  const handleImageSelect = (file: File) => {
    setSelectedImage(file);
    const url = URL.createObjectURL(file);
    setImagePreviewUrl(url);
  };

  const handleAnalyze = async () => {
    if (!selectedImage) {
      toast({
        title: "No image selected",
        description: "Please select an image to analyze.",
        variant: "destructive",
      });
      return;
    }

    try {
      setAppState('loading');
      setLoadingStage('predicting');

      // Step 1: Get pest prediction
      const predictionResult = await PestApiService.predictPest(selectedImage);
      setPrediction(predictionResult);
      
      setLoadingStage('analyzing');
      
      // Step 2: Get recommendations
      setLoadingStage('recommending');
      const topPest = predictionResult.predictions[0].class_name;
      const recommendationResult = await PestApiService.getRecommendations(topPest);
      setRecommendation(recommendationResult);

      // Step 3: Show results
      setAppState('results');
      
      toast({
        title: "Analysis Complete",
        description: `Detected ${recommendationResult.pest_name} with ${Math.round(predictionResult.predictions[0].confidence * 100)}% confidence.`,
      });

    } catch (error) {
      console.error('Analysis error:', error);
      toast({
        title: "Analysis Failed",
        description: "There was an error analyzing your image. Please try again.",
        variant: "destructive",
      });
      setAppState('upload');
    }
  };

  const handleBackToUpload = () => {
    setAppState('upload');
    setSelectedImage(null);
    if (imagePreviewUrl) {
      URL.revokeObjectURL(imagePreviewUrl);
      setImagePreviewUrl('');
    }
    setPrediction(null);
    setRecommendation(null);
  };

  if (appState === 'loading') {
    return <LoadingState stage={loadingStage} />;
  }

  if (appState === 'results' && prediction && recommendation) {
    return (
      <ResultsDisplay
        uploadedImage={imagePreviewUrl}
        prediction={prediction}
        recommendation={recommendation}
        onBackToUpload={handleBackToUpload}
      />
    );
  }

  // Default upload state
  return (
    <div className="min-h-screen bg-subtle-gradient">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-primary/90 to-primary-dark/90 text-white overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-20"
          style={{ backgroundImage: `url(${agriculturalHero})` }}
        />
        <div className="relative container mx-auto px-4 py-16 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            AI-Powered Pest Detection
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
            Upload an image of any pest affecting your crops and get instant identification 
            plus personalized treatment recommendations
          </p>
          <div className="flex flex-wrap justify-center gap-6 text-sm opacity-75">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span>Instant AI Analysis</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span>Organic & Chemical Solutions</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span>Prevention Strategies</span>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      <div className="container mx-auto px-4 py-16">
        <ImageUpload
          onImageSelect={handleImageSelect}
          onAnalyze={handleAnalyze}
          isLoading={false}
        />
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 pb-16">
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold">Accurate Identification</h3>
            <p className="text-muted-foreground">
              Advanced AI trained on thousands of pest images for precise identification
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto bg-success/10 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold">Eco-Friendly Options</h3>
            <p className="text-muted-foreground">
              Prioritized organic and IPM solutions to protect your crops naturally
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto bg-warning/10 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold">Expert Guidance</h3>
            <p className="text-muted-foreground">
              Comprehensive treatment plans and prevention strategies from agricultural experts
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};