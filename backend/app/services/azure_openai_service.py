"""
Azure OpenAI service for image embeddings and explanations
"""
import base64
import asyncio
from typing import List, Dict, Any
import httpx
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Service for Azure OpenAI operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=60.0)
        self.headers = {
            "api-key": self.settings.azure_openai_api_key,
            "Content-Type": "application/json"
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_image_embedding(self, image_data: bytes) -> List[float]:
        """
        Generate embedding for an image using Azure OpenAI Vision API
        
        Args:
            image_data: Image bytes
            
        Returns:
            List of embedding values
        """
        try:
            # Convert image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare the API request
            url = f"{self.settings.azure_openai_endpoint}/openai/deployments/{self.settings.azure_openai_deployment_name}/chat/completions"
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Generate a detailed description of this image that captures its visual elements, objects, colors, composition, and style."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.1
            }
            
            # Make API request
            response = await self.client.post(
                url,
                headers=self.headers,
                json=payload,
                params={"api-version": self.settings.azure_openai_api_version}
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenAI API error: {response.status_code}")
            
            result = response.json()
            description = result['choices'][0]['message']['content']
            
            # Generate embeddings from the description
            embedding = await self.generate_text_embedding(description)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating image embedding: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_text_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Azure OpenAI
        
        Args:
            text: Input text
            
        Returns:
            List of embedding values
        """
        try:
            url = f"{self.settings.azure_openai_endpoint}/openai/deployments/{self.settings.azure_openai_embedding_deployment_name}/embeddings"
            
            payload = {
                "input": text,
                "encoding_format": "float"
            }
            
            response = await self.client.post(
                url,
                headers=self.headers,
                json=payload,
                params={"api-version": self.settings.azure_openai_api_version}
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI embedding API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenAI embedding API error: {response.status_code}")
            
            result = response.json()
            embedding = result['data'][0]['embedding']
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating text embedding: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_similarity_explanation(self, query_image_data: bytes, similar_image_data: bytes) -> str:
        """
        Generate explanation for why two images are similar
        
        Args:
            query_image_data: Query image bytes
            similar_image_data: Similar image bytes
            
        Returns:
            Explanation text
        """
        try:
            # Convert images to base64
            query_base64 = base64.b64encode(query_image_data).decode('utf-8')
            similar_base64 = base64.b64encode(similar_image_data).decode('utf-8')
            
            url = f"{self.settings.azure_openai_endpoint}/openai/deployments/{self.settings.azure_openai_deployment_name}/chat/completions"
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Compare these two images and explain why they are visually similar in 1 short sentence. Focus on the most obvious visual similarity like objects, colors, or composition."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{query_base64}"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{similar_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.3
            }
            
            response = await self.client.post(
                url,
                headers=self.headers,
                json=payload,
                params={"api-version": self.settings.azure_openai_api_version}
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI explanation API error: {response.status_code} - {response.text}")
                return "Both images share similar visual characteristics and composition."
            
            result = response.json()
            explanation = result['choices'][0]['message']['content']
            
            return explanation.strip()
            
        except Exception as e:
            logger.error(f"Error generating similarity explanation: {str(e)}")
            return "Both images share similar visual characteristics and composition."
    
    def calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            # Convert to 0-1 range
            return float((similarity + 1) / 2)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
