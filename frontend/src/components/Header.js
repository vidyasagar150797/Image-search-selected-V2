import React from 'react';
import { Search, Cpu, Cloud } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 rounded-lg p-2">
              <Search className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Azure Image Search</h1>
              <p className="text-sm text-gray-500">AI-Powered Visual Discovery</p>
            </div>
          </div>

          {/* Technology Stack Badges */}
          <div className="hidden md:flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-gray-100 rounded-full px-3 py-1">
              <Cpu className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">Azure OpenAI</span>
            </div>
            <div className="flex items-center space-x-2 bg-gray-100 rounded-full px-3 py-1">
              <Cloud className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-gray-700">Cognitive Search</span>
            </div>
            <div className="flex items-center space-x-2 bg-gray-100 rounded-full px-3 py-1">
              <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-700">Blob Storage</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 