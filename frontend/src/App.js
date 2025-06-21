import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import ImageUpload from './components/ImageUpload';
import TextSearch from './components/TextSearch';
import CSVUpload from './components/CSVUpload';
import SearchResults from './components/SearchResults';
import Header from './components/Header';
import './App.css';

function App() {
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('image'); // 'image', 'text', or 'csv'

  const handleSearchComplete = (results) => {
    setSearchResults(results);
    setIsLoading(false);
  };

  const handleSearchStart = () => {
    setIsLoading(true);
    setSearchResults(null);
  };

  const switchTab = (tab) => {
    if (!isLoading) {
      setActiveTab(tab);
      setSearchResults(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
              AI-Powered 
              <span className="text-blue-600"> Image Search</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Search by uploading an image, describing what you're looking for, or bulk index images from CSV/Excel files. 
              Powered by Azure OpenAI and advanced computer vision.
            </p>
          </div>

          {/* Search Mode Tabs */}
          <div className="flex justify-center mb-8">
            <div className="bg-white rounded-xl p-2 shadow-lg">
              <button
                onClick={() => switchTab('image')}
                disabled={isLoading}
                className={`px-4 py-3 rounded-lg font-semibold transition-all ${
                  activeTab === 'image'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-blue-600 disabled:opacity-50'
                }`}
              >
                🖼️ Search by Image
              </button>
              <button
                onClick={() => switchTab('text')}
                disabled={isLoading}
                className={`px-4 py-3 rounded-lg font-semibold transition-all ${
                  activeTab === 'text'
                    ? 'bg-purple-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-purple-600 disabled:opacity-50'
                }`}
              >
                ✨ Search by Text
              </button>
              <button
                onClick={() => switchTab('csv')}
                disabled={isLoading}
                className={`px-4 py-3 rounded-lg font-semibold transition-all ${
                  activeTab === 'csv'
                    ? 'bg-green-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-green-600 disabled:opacity-50'
                }`}
              >
                📊 Bulk Index CSV
              </button>
            </div>
          </div>

          {/* Content Section */}
          <div className="mb-12">
            {activeTab === 'image' && (
              <ImageUpload 
                onSearchStart={handleSearchStart}
                onSearchComplete={handleSearchComplete}
                isLoading={isLoading}
              />
            )}
            {activeTab === 'text' && (
              <TextSearch 
                onSearchStart={handleSearchStart}
                onSearchComplete={handleSearchComplete}
                isLoading={isLoading}
              />
            )}
            {activeTab === 'csv' && (
              <CSVUpload />
            )}
          </div>

          {/* Results Section - Only show for search tabs */}
          {(searchResults || isLoading) && activeTab !== 'csv' && (
            <div className="mb-12">
              <SearchResults 
                results={searchResults} 
                isLoading={isLoading}
                searchType={activeTab}
              />
            </div>
          )}

          {/* Features Section */}
          {!searchResults && !isLoading && (
            <div className="grid md:grid-cols-4 gap-6 mt-16">
              <div className="text-center p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Visual Search</h3>
                <p className="text-gray-600">
                  Upload images to find visually similar matches using AI-powered analysis.
                </p>
              </div>

              <div className="text-center p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Text Search</h3>
                <p className="text-gray-600">
                  Describe what you're looking for in natural language and find matching images instantly.
                </p>
              </div>

              <div className="text-center p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Bulk Indexing</h3>
                <p className="text-gray-600">
                  Upload CSV/Excel files with image URLs to add thousands of images to the search index.
                </p>
              </div>

              <div className="text-center p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Lightning Fast</h3>
                <p className="text-gray-600">
                  Get results in seconds with optimized vector search across thousands of images.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            Powered by Azure OpenAI, Azure Cognitive Search, and Azure Blob Storage
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App; 