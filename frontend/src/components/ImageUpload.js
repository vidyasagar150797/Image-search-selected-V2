import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image as ImageIcon, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadImageAndSearch } from '../services/api';

const ImageUpload = ({ onSearchStart, onSearchComplete, isLoading }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedImage(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp', '.bmp']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB
    onError: (error) => {
      toast.error('Error uploading file: ' + error.message);
    }
  });

  const handleSearch = async () => {
    if (!selectedImage) {
      toast.error('Please select an image first');
      return;
    }

    onSearchStart();
    
    try {
      const results = await uploadImageAndSearch(selectedImage);
      onSearchComplete(results);
      toast.success('Search completed successfully!');
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Search failed: ' + error.message);
      onSearchComplete(null);
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      {!previewUrl ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          {isDragActive ? (
            <p className="text-lg text-blue-600 font-medium">Drop the image here...</p>
          ) : (
            <div>
              <p className="text-lg text-gray-700 font-medium mb-2">
                Drag & drop an image here, or click to select
              </p>
              <p className="text-sm text-gray-500">
                Supports JPG, PNG, WebP, BMP (max 10MB)
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Image Preview */}
          <div className="relative">
            <img
              src={previewUrl}
              alt="Preview"
              className="w-full max-w-md mx-auto rounded-lg shadow-md"
            />
            <button
              onClick={clearImage}
              className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 hover:bg-red-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Image Info */}
          <div className="text-center space-y-2">
            <p className="text-sm text-gray-600">
              <ImageIcon className="w-4 h-4 inline mr-1" />
              {selectedImage.name}
            </p>
            <p className="text-xs text-gray-500">
              {(selectedImage.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>

          {/* Search Button */}
          <div className="text-center">
            <button
              onClick={handleSearch}
              disabled={isLoading}
              className={`px-8 py-3 rounded-xl font-semibold text-white transition-all ${
                isLoading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Searching...
                </div>
              ) : (
                'Find Similar Images'
              )}
            </button>
          </div>

          {/* Change Image Button */}
          <div className="text-center">
            <button
              onClick={clearImage}
              className="text-sm text-gray-500 hover:text-gray-700 underline"
            >
              Choose a different image
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload; 