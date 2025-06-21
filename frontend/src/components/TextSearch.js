import React, { useState } from 'react';
import { Search, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { searchImagesByText } from '../services/api';

const TextSearch = ({ onSearchStart, onSearchComplete, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    onSearchStart();
    
    try {
      const results = await searchImagesByText(query.trim());
      onSearchComplete(results);
      toast.success('Search completed successfully!');
    } catch (error) {
      console.error('Text search error:', error);
      toast.error('Search failed: ' + error.message);
      onSearchComplete(null);
    }
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSearch(e);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <div className="text-center mb-6">
        <div className="flex items-center justify-center mb-3">
          <Sparkles className="w-8 h-8 text-purple-600 mr-3" />
          <h3 className="text-2xl font-bold text-gray-900">Search by Description</h3>
        </div>
        <p className="text-gray-600">
          Describe what you're looking for and find matching images
        </p>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="e.g., sunset over mountains, red sports car, cute puppy playing..."
            className="w-full pl-12 pr-4 py-4 border border-gray-300 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className={`w-full py-4 rounded-xl font-semibold text-white text-lg transition-all ${
            isLoading || !query.trim()
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-purple-600 hover:bg-purple-700 hover:shadow-lg'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
              Searching Images...
            </div>
          ) : (
            <div className="flex items-center justify-center">
              <Search className="w-5 h-5 mr-2" />
              Search Images
            </div>
          )}
        </button>
      </form>

      {/* Example queries */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-sm text-gray-500 mb-3">Try these examples:</p>
        <div className="flex flex-wrap gap-2">
          {[
            'beautiful landscape',
            'modern architecture',
            'colorful flowers',
            'vintage car',
            'ocean sunset'
          ].map((example) => (
            <button
              key={example}
              onClick={() => setQuery(example)}
              disabled={isLoading}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TextSearch; 