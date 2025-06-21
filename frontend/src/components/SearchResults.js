import React from 'react';
import { Clock, Zap, Search, Image as ImageIcon } from 'lucide-react';

const SearchResults = ({ results, isLoading, searchType = 'image' }) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <h3 className="text-2xl font-semibold text-gray-900 mb-2">
            {searchType === 'image' ? 'Analyzing Image...' : 'Searching Images...'}
          </h3>
          <p className="text-gray-600">
            {searchType === 'image' 
              ? 'AI is analyzing your image and finding similar matches'
              : 'AI is understanding your query and finding matching images'
            }
          </p>
        </div>
      </div>
    );
  }

  if (!results || !results.similar_images || results.similar_images.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
        <div className="text-gray-400 mb-4">
          <Search className="w-16 h-16 mx-auto" />
        </div>
        <h3 className="text-2xl font-semibold text-gray-900 mb-2">No Results Found</h3>
        <p className="text-gray-600">
          {searchType === 'image' 
            ? 'No similar images found. Try uploading a different image.'
            : 'No matching images found. Try a different search query.'
          }
        </p>
      </div>
    );
  }

  const { similar_images, search_time, query } = results;
  const isTextSearch = searchType === 'text';

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      {/* Results Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          {isTextSearch ? (
            <Search className="w-8 h-8 text-purple-600 mr-3" />
          ) : (
            <ImageIcon className="w-8 h-8 text-blue-600 mr-3" />
          )}
          <h2 className="text-3xl font-bold text-gray-900">
            {isTextSearch ? 'Text Search Results' : 'Similar Images Found'}
          </h2>
        </div>
        
        {isTextSearch && query && (
          <div className="bg-gray-50 rounded-lg p-3 mb-4 inline-block">
            <p className="text-gray-700">
              <span className="font-medium">Search query:</span> "{query}"
            </p>
          </div>
        )}
        
        <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center">
            <Zap className="w-4 h-4 mr-1" />
            <span>{similar_images.length} results</span>
          </div>
          {search_time && (
            <div className="flex items-center">
              <Clock className="w-4 h-4 mr-1" />
              <span>{search_time.toFixed(2)}s</span>
            </div>
          )}
        </div>
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {similar_images.map((image, index) => (
          <div
            key={image.image_id}
            className="bg-gray-50 rounded-xl overflow-hidden hover:shadow-lg transition-shadow duration-300"
          >
            {/* Image */}
            <div className="relative">
              <img
                src={image.image_url}
                alt={`Similar image ${index + 1}`}
                className="w-full h-48 object-cover"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xMDAgNzVIMjAwVjEyNUgxMDBWNzVaIiBmaWxsPSIjRTVFN0VCIi8+CjxjaXJjbGUgY3g9IjEzMCIgY3k9IjEwMCIgcj0iMTAiIGZpbGw9IiNEMUQ1REIiLz4KPHBhdGggZD0iTTE0MCAzNUwyMDAgNzVIMTQwVjM1WiIgZmlsbD0iI0Q2REFEOSIvPgo8L3N2Zz4K';
                  e.target.alt = 'Image not found';
                }}
              />
              {/* Similarity Score Badge */}
              <div className="absolute top-2 right-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium text-white ${
                  image.similarity_score > 0.8 
                    ? 'bg-green-500' 
                    : image.similarity_score > 0.6 
                      ? 'bg-yellow-500' 
                      : 'bg-red-500'
                }`}>
                  {(image.similarity_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Content */}
            <div className="p-4">
              <div className="mb-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-500">
                    Match #{index + 1}
                  </span>
                  <span className="text-sm text-gray-400">
                    Score: {image.similarity_score.toFixed(3)}
                  </span>
                </div>
              </div>
              
              {/* Explanation */}
              <p className="text-sm text-gray-700 leading-relaxed">
                {image.explanation}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Additional Info */}
      <div className="mt-8 pt-6 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-500">
          {isTextSearch 
            ? 'Results are ranked by semantic similarity to your text description'
            : 'Results are ranked by visual similarity to your uploaded image'
          }
        </p>
      </div>
    </div>
  );
};

export default SearchResults; 