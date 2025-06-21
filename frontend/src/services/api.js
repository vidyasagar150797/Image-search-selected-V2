import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 60000, // 60 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`Response received from: ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with an error status
      const message = error.response.data?.detail || 
                     error.response.data?.message || 
                     `Server error: ${error.response.status}`;
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

/**
 * Upload an image and search for similar images
 * @param {File} imageFile - The image file to upload
 * @param {number} topK - Number of similar images to return (default: 5)
 * @returns {Promise<Object>} - Search results
 */
export const uploadImageAndSearch = async (imageFile, topK = 5) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    params: {
      top_k: topK,
    },
  });
  
  return response.data;
};

/**
 * Search for images using text query
 * @param {string} query - Text query
 * @param {number} topK - Number of results to return
 * @returns {Promise<Object>} - Search results
 */
export const searchImages = async (query, topK = 5) => {
  const response = await api.post('/search', {
    query,
    top_k: topK,
  });
  
  return response.data;
};

/**
 * Index images from URLs (Admin function)
 * @param {string[]} imageUrls - Array of image URLs to index
 * @param {number} batchSize - Batch size for processing
 * @returns {Promise<Object>} - Indexing response
 */
export const indexImages = async (imageUrls, batchSize = 10) => {
  const response = await api.post('/index', {
    image_urls: imageUrls,
    batch_size: batchSize,
  });
  
  return response.data;
};

/**
 * Get system health status
 * @returns {Promise<Object>} - Health status
 */
export const getHealthStatus = async () => {
  const response = await api.get('/health');
  return response.data;
};

/**
 * Get system statistics
 * @returns {Promise<Object>} - System stats
 */
export const getSystemStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export default api; 