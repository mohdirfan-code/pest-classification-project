// src/services/pestApi.ts

export interface PredictionResponse {
  filename: string;
  predictions: {
    class_name: string;
    confidence: number;
  }[];
}

export interface RecommendationResponse {
  pest_name: string;
  pest_info: string;
  ipm_solutions: string[];
  chemical_solutions: {
    pesticide: string;
    dosage: string;
    notes: string;
  }[];
  prevention_tips: string[];
}

export class PestApiService {
  // This URL must point to your running FastAPI server
  private static baseUrl = 'http://127.0.0.1:8000';

  static async predictPest(imageFile: File): Promise<PredictionResponse> {
    const formData = new FormData();
    formData.append('file', imageFile);

    const response = await fetch(`${this.baseUrl}/predict`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Prediction failed');
    }

    return response.json();
  }

  static async getRecommendations(pestName: string): Promise<RecommendationResponse> {
    const response = await fetch(`${this.baseUrl}/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pest_name: pestName }),
    });

    if (!response.ok) {
        const errorData = await response.json();
      throw new Error(errorData.detail || 'Recommendation failed');
    }

    return response.json();
  }
}