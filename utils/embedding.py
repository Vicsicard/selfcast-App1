"""
Text embedding utilities using OpenAI's API.
"""
from typing import List
import openai
from loguru import logger

class EmbeddingGenerator:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text using OpenAI's API.
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding
        """
        try:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []
            
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            if embedding:
                embeddings.append(embedding)
        return embeddings
