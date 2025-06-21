# Azure Image Search Application

An enterprise-grade visual search system that enables users to find visually similar images using natural language queries, powered by Azure OpenAI, Azure Cognitive Search, and Azure Blob Storage.

## 🚀 Features

- **AI-Powered Image Analysis**: Uses Azure OpenAI Vision API to understand image content
- **Semantic Search**: Find similar images using advanced vector search capabilities
- **Smart Explanations**: AI-generated explanations for why images are similar
- **Scalable Architecture**: Built for enterprise-scale deployment
- **Modern UI**: Clean, responsive React frontend with Tailwind CSS
- **Enterprise Security**: Integrated with Azure services for security and compliance

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   Azure Services │
│                 │    │                 │    │                 │
│ • Image Upload  │◄──►│ • Image Processing│◄──►│ • OpenAI Vision │
│ • Search UI     │    │ • Vector Search  │    │ • Blob Storage  │
│ • Results Display│    │ • API Endpoints  │    │ • Cognitive Search│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Azure OpenAI**: GPT-4 Vision for image analysis and embeddings
- **Azure Blob Storage**: Scalable image storage
- **Azure Cognitive Search**: Vector search capabilities
- **Python 3.12**: Latest Python version

### Frontend
- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **React Dropzone**: File upload functionality
- **Lucide React**: Modern icon library

### Deployment
- **Docker**: Containerization for both services
- **Docker Compose**: Local development orchestration
- **Nginx**: Production-ready web server
- **Azure Container Instances**: Cloud deployment

## 📋 Prerequisites

Before setting up the application, ensure you have:

1. **Azure Account** with active subscription
2. **Docker** and **Docker Compose** installed
3. **Node.js** 18+ and **npm** (for local development)
4. **Python** 3.12+ (for local development)
5. **Azure CLI** (for deployment)

## ☁️ Azure Services Setup

### 1. Azure OpenAI Service

```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --name "your-openai-service" \
  --resource-group "your-resource-group" \
  --location "eastus" \
  --kind "OpenAI" \
  --sku "s0"

# Deploy models
az cognitiveservices account deployment create \
  --name "your-openai-service" \
  --resource-group "your-resource-group" \
  --deployment-name "gpt-4-vision-preview" \
  --model-name "gpt-4-vision-preview" \
  --model-version "1" \
  --model-format "OpenAI" \
  --scale-settings-scale-type "Standard"

az cognitiveservices account deployment create \
  --name "your-openai-service" \
  --resource-group "your-resource-group" \
  --deployment-name "text-embedding-ada-002" \
  --model-name "text-embedding-ada-002" \
  --model-version "2" \
  --model-format "OpenAI" \
  --scale-settings-scale-type "Standard"
```

### 2. Azure Blob Storage

```bash
# Create storage account
az storage account create \
  --name "yourstorageaccount" \
  --resource-group "your-resource-group" \
  --location "eastus" \
  --sku "Standard_LRS"

# Create container for images
az storage container create \
  --name "images" \
  --account-name "yourstorageaccount"
```

### 3. Azure Cognitive Search

```bash
# Create search service
az search service create \
  --name "your-search-service" \
  --resource-group "your-resource-group" \
  --location "eastus" \
  --sku "standard"
```

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Image-search-selected-V2
```

### 2. Environment Configuration

Copy the environment template and fill in your Azure credentials:

```bash
cp env.template .env
```

Edit `.env` file with your Azure service credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-vision-preview

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=your_blob_storage_connection_string_here
AZURE_STORAGE_CONTAINER=images

# Azure Cognitive Search Configuration
AZURE_SEARCH_API_KEY=your_cognitive_search_api_key_here
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net/
AZURE_SEARCH_INDEX_NAME=image-index
```

### 3. Quick Start with Docker Compose

```bash
# Build and start all services
cd deployment
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 4. Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📚 API Documentation

### Upload and Search Images

```bash
# Upload an image and find similar images
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg" \
  -F "top_k=5"
```

### Index Images (Admin)

```bash
# Index images from URLs
curl -X POST "http://localhost:8000/index" \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": [
      "https://example.com/image1.jpg",
      "https://example.com/image2.jpg"
    ],
    "batch_size": 10
  }'
```

### Text-based Search

```bash
# Search using text query
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sunset over mountains",
    "top_k": 5
  }'
```

## 🚀 Deployment

### Azure Container Instances

1. **Build and push images to Azure Container Registry**:

```bash
# Login to Azure
az login

# Create ACR
az acr create --resource-group "your-resource-group" --name "youracr" --sku Basic

# Build and push backend
cd backend
az acr build --registry "youracr" --image image-search-backend:latest .

# Build and push frontend
cd ../frontend
az acr build --registry "youracr" --image image-search-frontend:latest .
```

2. **Deploy to Azure Container Instances**:

```bash
# Deploy backend
az container create \
  --resource-group "your-resource-group" \
  --name "image-search-backend" \
  --image "youracr.azurecr.io/image-search-backend:latest" \
  --registry-login-server "youracr.azurecr.io" \
  --registry-username "youracr" \
  --registry-password "your-acr-password" \
  --dns-name-label "image-search-api" \
  --ports 8000 \
  --environment-variables \
    AZURE_OPENAI_API_KEY="your-key" \
    AZURE_OPENAI_ENDPOINT="your-endpoint" \
    # ... other environment variables

# Deploy frontend
az container create \
  --resource-group "your-resource-group" \
  --name "image-search-frontend" \
  --image "youracr.azurecr.io/image-search-frontend:latest" \
  --registry-login-server "youracr.azurecr.io" \
  --registry-username "youracr" \
  --registry-password "your-acr-password" \
  --dns-name-label "image-search-app" \
  --ports 80 \
  --environment-variables \
    REACT_APP_API_URL="https://image-search-api.eastus.azurecontainer.io:8000"
```

### Azure App Service

1. **Create App Service Plan**:

```bash
az appservice plan create \
  --name "image-search-plan" \
  --resource-group "your-resource-group" \
  --is-linux \
  --sku B1
```

2. **Deploy Backend**:

```bash
az webapp create \
  --resource-group "your-resource-group" \
  --plan "image-search-plan" \
  --name "image-search-backend-app" \
  --deployment-container-image-name "youracr.azurecr.io/image-search-backend:latest"

# Configure app settings
az webapp config appsettings set \
  --resource-group "your-resource-group" \
  --name "image-search-backend-app" \
  --settings \
    AZURE_OPENAI_API_KEY="your-key" \
    AZURE_OPENAI_ENDPOINT="your-endpoint" \
    # ... other settings
```

## 🔍 Usage

### 1. Upload and Search

1. Navigate to the application in your browser
2. Drag and drop an image or click to select
3. Click "Find Similar Images" 
4. View results with AI-generated explanations

### 2. Index Images

Use the `/index` endpoint to add images to the search database:

```python
import requests

# Index images from the provided CSV
response = requests.post(
    "http://localhost:8000/index",
    json={
        "image_urls": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ],
        "batch_size": 10
    }
)
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | ✅ |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | ✅ |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment name | ✅ |
| `AZURE_STORAGE_CONNECTION_STRING` | Blob storage connection string | ✅ |
| `AZURE_SEARCH_API_KEY` | Cognitive Search API key | ✅ |
| `AZURE_SEARCH_ENDPOINT` | Cognitive Search endpoint | ✅ |
| `MAX_FILE_SIZE` | Maximum upload file size (bytes) | ❌ |
| `SEARCH_TOP_K` | Default number of results | ❌ |

### Performance Tuning

- **Batch Size**: Adjust `batch_size` in indexing requests
- **Top K**: Configure number of results returned
- **Timeout**: Adjust API timeout settings for large images
- **Concurrency**: Configure FastAPI worker processes

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

### API Health Check

```bash
curl http://localhost:8000/health
```

## 📊 Monitoring

### Health Endpoints

- Backend: `GET /health`
- Frontend: `GET /health` (nginx)

### Metrics

- Upload success rate
- Search latency
- Index size
- API response times

## 🛡️ Security

- API key authentication for Azure services
- CORS configuration for frontend
- Input validation and sanitization
- Rate limiting (configurable)
- Secure headers in nginx

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the [troubleshooting guide](#troubleshooting)
2. Review [Azure service documentation](https://docs.microsoft.com/azure/)
3. Create an issue in the repository

## 🔧 Troubleshooting

### Common Issues

**1. Azure OpenAI Rate Limits**
```
Error: Rate limit exceeded
Solution: Implement retry logic or upgrade to higher tier
```

**2. Blob Storage Permissions**
```
Error: Authorization failed
Solution: Check connection string and container permissions
```

**3. Search Index Not Found**
```
Error: Index not found
Solution: Ensure search service is running and index is created
```

**4. CORS Issues**
```
Error: CORS policy blocked
Solution: Update CORS settings in FastAPI configuration
```

### Performance Issues

- **Slow Search**: Check search service tier and index size
- **Large Images**: Implement image compression
- **Memory Usage**: Monitor container resources

## 🎯 Next Steps

- [ ] Add user authentication
- [ ] Implement image categorization
- [ ] Add batch processing UI
- [ ] Enhance search filters
- [ ] Add analytics dashboard
- [ ] Implement caching layer 