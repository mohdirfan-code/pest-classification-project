import React, { useState } from 'react';
import { ArrowLeft, CheckCircle, AlertTriangle, Leaf, Beaker, Shield, Camera, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { PredictionResponse, RecommendationResponse } from '@/services/pestApi';

interface ResultsDisplayProps {
  uploadedImage: string;
  prediction: PredictionResponse;
  recommendation: RecommendationResponse;
  onBackToUpload: () => void;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  uploadedImage,
  prediction,
  recommendation,
  onBackToUpload
}) => {
  const [activeTab, setActiveTab] = useState('organic');
  
  const topPrediction = prediction.predictions[0];
  const confidencePercentage = Math.round(topPrediction.confidence * 100);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-success';
    if (confidence >= 0.6) return 'text-warning';
    return 'text-danger';
  };

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.8) return { variant: 'default' as const, text: 'High Confidence' };
    if (confidence >= 0.6) return { variant: 'secondary' as const, text: 'Medium Confidence' };
    return { variant: 'destructive' as const, text: 'Low Confidence' };
  };

  const confidenceBadge = getConfidenceBadge(topPrediction.confidence);

  return (
    <div className="min-h-screen bg-subtle-gradient py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button
            onClick={onBackToUpload}
            variant="outline"
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            New Analysis
          </Button>
          <h1 className="text-2xl font-bold text-foreground">Pest Analysis Results</h1>
          <div></div>
        </div>

        {/* Identification Section */}
        <Card className="mb-8 shadow-soft">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="w-5 h-5 text-primary" />
              Pest Identification
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-8">
              {/* Uploaded Image */}
              <div className="space-y-4">
                <h3 className="font-semibold text-lg">Your Image</h3>
                <img
                  src={uploadedImage}
                  alt="Uploaded pest"
                  className="w-full rounded-lg border shadow-sm max-h-80 object-contain bg-muted/50"
                />
              </div>

              {/* Prediction Results */}
              <div className="space-y-6">
                <div className="bg-gradient-to-br from-primary/5 to-primary/10 p-6 rounded-lg border border-primary/20">
                  <div className="flex items-center gap-3 mb-6">
                    <h2 className="text-3xl font-bold text-foreground">
                      {recommendation.pest_name}
                    </h2>
                    <Badge variant={confidenceBadge.variant}>
                      {confidenceBadge.text}
                    </Badge>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-primary" />
                      <span className="font-medium">Confidence Score:</span>
                      <span className={`font-bold text-lg ${getConfidenceColor(topPrediction.confidence)}`}>
                        {confidencePercentage}%
                      </span>
                    </div>
                    
                    <div className="pt-4 border-t border-primary/20">
                      <p className="text-sm text-muted-foreground mb-2">Analysis Details:</p>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Detection Method:</span>
                          <p className="text-muted-foreground">AI Image Recognition</p>
                        </div>
                        <div>
                          <span className="font-medium">Classification:</span>
                          <p className="text-muted-foreground capitalize">{topPrediction.class_name.replace('_', ' ')}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* About Section */}
        <Card className="mb-8 shadow-soft">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-warning" />
              About This Pest
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-foreground leading-relaxed text-lg">
              {recommendation.pest_info}
            </p>
          </CardContent>
        </Card>

        {/* Treatment Plans */}
        <Card className="mb-8 shadow-soft">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Beaker className="w-5 h-5 text-primary" />
              Treatment Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-1 sm:grid-cols-2 mb-6">
                <TabsTrigger value="organic" className="flex items-center justify-center gap-2 text-sm">
                  <Leaf className="w-4 h-4" />
                  <span className="hidden sm:inline">Organic/IPM Solutions</span>
                  <span className="sm:hidden">Organic</span>
                </TabsTrigger>
                <TabsTrigger value="chemical" className="flex items-center justify-center gap-2 text-sm">
                  <Beaker className="w-4 h-4" />
                  <span className="hidden sm:inline">Chemical Solutions</span>
                  <span className="sm:hidden">Chemical</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="organic" className="space-y-4">
                <div className="grid gap-4">
                  {recommendation.ipm_solutions.map((solution, index) => (
                    <div key={index} className="flex items-start gap-3 p-4 bg-success/5 border border-success/20 rounded-lg">
                      <CheckCircle className="w-5 h-5 text-success mt-0.5 flex-shrink-0" />
                      <p className="text-foreground">{solution}</p>
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="chemical" className="space-y-4">
                {/* Desktop Table View */}
                <div className="hidden md:block overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-4 font-semibold text-foreground">Pesticide (Active Ingredient)</th>
                        <th className="text-left p-4 font-semibold text-foreground">Recommended Dosage</th>
                        <th className="text-left p-4 font-semibold text-foreground">Safety Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recommendation.chemical_solutions.map((solution, index) => (
                        <tr key={index} className="border-b hover:bg-muted/30">
                          <td className="p-4 font-medium text-foreground">{solution.pesticide}</td>
                          <td className="p-4 text-foreground">{solution.dosage}</td>
                          <td className="p-4 text-sm text-muted-foreground">{solution.notes}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {/* Mobile Card View */}
                <div className="md:hidden space-y-4">
                  {recommendation.chemical_solutions.map((solution, index) => (
                    <div key={index} className="bg-muted/30 rounded-lg p-4 space-y-3">
                      <h4 className="font-semibold text-foreground text-lg">{solution.pesticide}</h4>
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm font-medium text-muted-foreground">Dosage:</span>
                          <p className="text-foreground">{solution.dosage}</p>
                        </div>
                        <div>
                          <span className="text-sm font-medium text-muted-foreground">Safety Notes:</span>
                          <p className="text-sm text-muted-foreground">{solution.notes}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Prevention Tips */}
        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-success" />
              Prevention Tips
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              {recommendation.prevention_tips.map((tip, index) => (
                <div key={index} className="flex items-start gap-3 p-4 bg-primary/5 border border-primary/20 rounded-lg">
                  <Shield className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <p className="text-foreground">{tip}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Action Button */}
        <div className="text-center mt-8">
          <Button
            onClick={onBackToUpload}
            size="lg"
            variant="agricultural"
            className="px-8"
          >
            Analyze Another Image
          </Button>
        </div>
      </div>
    </div>
  );
};