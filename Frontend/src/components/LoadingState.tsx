import React from 'react';
import { Loader2, Microscope, Brain, Zap } from 'lucide-react';

interface LoadingStateProps {
  stage: 'predicting' | 'analyzing' | 'recommending';
}

export const LoadingState: React.FC<LoadingStateProps> = ({ stage }) => {
  const getStageInfo = () => {
    switch (stage) {
      case 'predicting':
        return {
          icon: <Microscope className="w-8 h-8" />,
          title: "Analyzing Image",
          description: "Our AI is examining your image to identify the pest..."
        };
      case 'analyzing':
        return {
          icon: <Brain className="w-8 h-8" />,
          title: "Processing Results",
          description: "Comparing with our pest database and determining confidence levels..."
        };
      case 'recommending':
        return {
          icon: <Zap className="w-8 h-8" />,
          title: "Generating Recommendations",
          description: "Creating personalized treatment plans and prevention strategies..."
        };
      default:
        return {
          icon: <Loader2 className="w-8 h-8" />,
          title: "Processing",
          description: "Please wait while we analyze your image..."
        };
    }
  };

  const stageInfo = getStageInfo();

  return (
    <div className="flex min-h-screen items-center justify-center bg-subtle-gradient">
      <div className="text-center space-y-8 p-8">
        {/* Animated Icon */}
        <div className="relative">
          <div className="mx-auto w-24 h-24 agricultural-gradient rounded-full flex items-center justify-center shadow-agricultural">
            <div className="text-white animate-pulse">
              {stageInfo.icon}
            </div>
          </div>
          
          {/* Rotating Border */}
          <div className="absolute inset-0 w-24 h-24 mx-auto border-4 border-transparent border-t-primary rounded-full animate-spin" />
        </div>

        {/* Content */}
        <div className="space-y-4 max-w-md">
          <h2 className="text-2xl font-semibold text-foreground">
            {stageInfo.title}
          </h2>
          <p className="text-muted-foreground text-lg">
            {stageInfo.description}
          </p>
        </div>

        {/* Progress Dots */}
        <div className="flex justify-center space-x-2">
          {[0, 1, 2].map((index) => (
            <div
              key={index}
              className="w-3 h-3 bg-primary rounded-full animate-bounce"
              style={{
                animationDelay: `${index * 0.2}s`,
                animationDuration: '1s'
              }}
            />
          ))}
        </div>

        {/* Tips */}
        <div className="bg-muted/50 rounded-lg p-4 max-w-md mx-auto">
          <p className="text-sm text-muted-foreground">
            💡 <strong>Tip:</strong> For best results, ensure your image shows the pest clearly 
            with good lighting and minimal background distractions.
          </p>
        </div>
      </div>
    </div>
  );
};