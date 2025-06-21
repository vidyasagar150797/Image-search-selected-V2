import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle2, X, Settings, Clock } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadCSVWithProgress, getUploadProgress } from '../services/api';

const CSVUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [columnName, setColumnName] = useState('url');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [progress, setProgress] = useState(null);
  const [taskId, setTaskId] = useState(null);

  // Poll for progress updates
  useEffect(() => {
    let interval;
    if (taskId && isUploading) {
      interval = setInterval(async () => {
        try {
          const progressData = await getUploadProgress(taskId);
          setProgress(progressData);
          
          if (progressData.status === 'completed' || progressData.status === 'error') {
            setIsUploading(false);
            clearInterval(interval);
            
            if (progressData.status === 'completed') {
              const successCount = progressData.current - progressData.errors.length;
              setUploadResults({
                message: `Processing completed! ${successCount}/${progressData.total} images indexed successfully.`,
                total_urls: progressData.total,
                successful_indexes: successCount,
                failed_urls: progressData.errors,
                processing_time: null
              });
              toast.success(`Successfully indexed ${successCount} images!`);
            } else {
              toast.error('Upload failed');
            }
          }
        } catch (error) {
          console.error('Error fetching progress:', error);
        }
      }, 2000); // Poll every 2 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [taskId, isUploading]);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setUploadResults(null);
      setProgress(null);
      setTaskId(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: false,
    maxSize: 50 * 1024 * 1024, // 50MB
    onError: (error) => {
      toast.error('Error uploading file: ' + error.message);
    }
  });

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file first');
      return;
    }

    if (!columnName.trim()) {
      toast.error('Please specify the column name containing URLs');
      return;
    }

    setIsUploading(true);
    setUploadResults(null);
    setProgress(null);
    
    try {
      const initResponse = await uploadCSVWithProgress(selectedFile, columnName.trim());
      setTaskId(initResponse.task_id);
      toast.success('Upload started! Processing images...');
      
    } catch (error) {
      console.error('CSV upload error:', error);
      toast.error('Upload failed: ' + error.message);
      setIsUploading(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setUploadResults(null);
    setProgress(null);
    setTaskId(null);
  };

  const getFileIcon = (filename) => {
    if (filename.toLowerCase().endsWith('.csv')) {
      return '📄';
    } else if (filename.toLowerCase().endsWith('.xlsx') || filename.toLowerCase().endsWith('.xls')) {
      return '📊';
    }
    return '📁';
  };

  const getProgressPercentage = () => {
    if (!progress || progress.total === 0) return 0;
    return Math.round((progress.current / progress.total) * 100);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <div className="text-center mb-6">
        <div className="flex items-center justify-center mb-3">
          <Upload className="w-8 h-8 text-green-600 mr-3" />
          <h3 className="text-2xl font-bold text-gray-900">Bulk Image Indexing</h3>
        </div>
        <p className="text-gray-600">
          Upload a CSV or Excel file with image URLs to add them to the search index
        </p>
      </div>

      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 hover:border-green-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          {isDragActive ? (
            <p className="text-lg text-green-600 font-medium">Drop the file here...</p>
          ) : (
            <div>
              <p className="text-lg text-gray-700 font-medium mb-2">
                Drag & drop a CSV/Excel file here, or click to select
              </p>
              <p className="text-sm text-gray-500">
                Supports .csv, .xlsx, .xls files (max 50MB)
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* File Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <span className="text-2xl mr-3">{getFileIcon(selectedFile.name)}</span>
                <div>
                  <p className="font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={clearFile}
                className="text-red-500 hover:text-red-700 p-1"
                disabled={isUploading}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Progress Display */}
          {isUploading && progress && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-blue-900">Processing Progress</h4>
                <span className="text-sm text-blue-700">{getProgressPercentage()}%</span>
              </div>
              
              {/* Progress Bar */}
              <div className="w-full bg-blue-200 rounded-full h-3 mb-4">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${getProgressPercentage()}%` }}
                ></div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-blue-700 font-medium">Images Processed:</span>
                  <span className="ml-2 text-blue-900">{progress.current} / {progress.total}</span>
                </div>
                <div>
                  <span className="text-blue-700 font-medium">Status:</span>
                  <span className="ml-2 text-blue-900 capitalize">{progress.status}</span>
                </div>
              </div>
              
              {progress.current_url && (
                <div className="mt-3 text-xs text-blue-600">
                  <span className="font-medium">Currently processing:</span>
                  <div className="truncate mt-1">{progress.current_url}</div>
                </div>
              )}
              
              {progress.errors.length > 0 && (
                <div className="mt-3 text-xs text-red-600">
                  <span className="font-medium">Failed URLs:</span>
                  <span className="ml-2">{progress.errors.length}</span>
                </div>
              )}
            </div>
          )}

          {/* Settings */}
          <div className="border rounded-lg p-4">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="flex items-center text-gray-700 hover:text-gray-900 mb-2"
              disabled={isUploading}
            >
              <Settings className="w-4 h-4 mr-2" />
              <span className="font-medium">Settings</span>
            </button>
            
            {showSettings && (
              <div className="ml-6 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Column name containing URLs
                  </label>
                  <input
                    type="text"
                    value={columnName}
                    onChange={(e) => setColumnName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="url"
                    disabled={isUploading}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Default: "url" (case-sensitive)
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className={`w-full py-4 rounded-xl font-semibold text-white text-lg transition-all ${
              isUploading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 hover:shadow-lg'
            }`}
          >
            {isUploading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                Processing Images...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <Upload className="w-5 h-5 mr-2" />
                Start Indexing
              </div>
            )}
          </button>

          {/* Change File Button */}
          <div className="text-center">
            <button
              onClick={clearFile}
              disabled={isUploading}
              className="text-sm text-gray-500 hover:text-gray-700 underline"
            >
              Choose a different file
            </button>
          </div>
        </div>
      )}

      {/* Upload Results */}
      {uploadResults && (
        <div className="mt-8 border-t pt-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Upload Results</h4>
          
          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-blue-600">{uploadResults.total_urls}</p>
              <p className="text-sm text-blue-800">Total URLs</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-green-600">{uploadResults.successful_indexes}</p>
              <p className="text-sm text-green-800">Successfully Indexed</p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-red-600">{uploadResults.failed_urls.length}</p>
              <p className="text-sm text-red-800">Failed URLs</p>
            </div>
          </div>

          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center text-green-600">
              <CheckCircle2 className="w-5 h-5 mr-2" />
              <span className="font-medium">{uploadResults.message}</span>
            </div>
          </div>

          {/* Failed URLs */}
          {uploadResults.failed_urls.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center mb-2">
                <AlertCircle className="w-4 h-4 text-red-600 mr-2" />
                <span className="font-medium text-red-800">Failed URLs ({uploadResults.failed_urls.length})</span>
              </div>
              <div className="max-h-32 overflow-y-auto">
                {uploadResults.failed_urls.slice(0, 10).map((url, index) => (
                  <p key={index} className="text-xs text-red-700 truncate">
                    {url}
                  </p>
                ))}
                {uploadResults.failed_urls.length > 10 && (
                  <p className="text-xs text-red-600 italic">
                    ... and {uploadResults.failed_urls.length - 10} more
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h5 className="font-medium text-gray-900 mb-2">File Format Requirements:</h5>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• CSV files should have a header row with column names</li>
          <li>• Excel files (.xlsx/.xls) are also supported</li>
          <li>• Default column name is "url" (you can change this in settings)</li>
          <li>• Each URL should point directly to an image file</li>
          <li>• Invalid URLs will be skipped automatically</li>
          <li>• Processing includes 3-second delays to avoid API rate limits</li>
        </ul>
      </div>
    </div>
  );
};

export default CSVUpload; 