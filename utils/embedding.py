"""
Text embedding utilities using sentence-transformers.
"""
from typing import List
from sentence_transformers import SentenceTransformer
from loguru import logger

class EmbeddingGenerator:
    def __init__(self):
        """Initialize the embedding model."""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text using sentence-transformers.
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding (384 dimensions)
        """
        try:
            # Generate embedding and convert to list of floats
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
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
