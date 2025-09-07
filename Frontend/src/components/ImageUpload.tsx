import React, { useState, useRef } from 'react';
import { Upload, Camera, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ImageUploadProps {
  onImageSelect: (file: File) => void;
  onAnalyze: () => void;
  isLoading: boolean;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({ onImageSelect, onAnalyze, isLoading }) => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      onImageSelect(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Upload Zone */}
      <div
        className={`upload-zone ${isDragOver ? 'dragover' : ''} relative`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileInputChange}
          className="hidden"
        />

        {!previewUrl ? (
          <div className="text-center">
            <div className="mx-auto w-16 h-16 mb-4 bg-primary/10 rounded-full flex items-center justify-center">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-foreground">
              Upload Pest Image
            </h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Upload an image of the pest on your crop to get an instant analysis and treatment plan. 
              Supported formats: JPG, PNG, WebP
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button 
                onClick={triggerFileSelect}
                variant="default"
                size="lg"
                className="px-8"
              >
                <Camera className="w-5 h-5 mr-2" />
                Choose Image
              </Button>
              <p className="text-sm text-muted-foreground flex items-center">
                or drag and drop your image here
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={previewUrl}
                alt="Selected pest"
                className="w-full max-h-96 object-contain rounded-lg"
              />
              <Button
                onClick={handleRemoveImage}
                variant="destructive"
                size="sm"
                className="absolute top-2 right-2"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-4">
                {selectedImage?.name} ({(selectedImage?.size || 0 / 1024 / 1024).toFixed(2)} MB)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Analyze Button */}
      {selectedImage && (
        <div className="text-center">
          <Button
            onClick={onAnalyze}
            disabled={isLoading}
            size="lg"
            variant="agricultural"
            className="px-12 py-3 text-lg font-semibold disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </>
            ) : (
              'Analyze Pest'
            )}
          </Button>
        </div>
      )}
    </div>
  );
};