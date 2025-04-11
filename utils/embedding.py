"""
Text embedding utilities for generating and storing chunk vectors.
"""
from typing import List, Dict, Union
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from loguru import logger

class EmbeddingGenerator:
    """Handles generation and storage of text embeddings for transcript chunks."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the embedding model.
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Initialized embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
        
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text using sentence-transformers.
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            # Clean and prepare text
            text = text.strip()
            if not text:
                raise ValueError("Empty text provided")
                
            # Generate embedding and convert to list of floats
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []
            
    def process_chunks(self, chunks: List[Dict], output_dir: Path) -> List[Dict]:
        """Process chunks and generate embeddings.
        
        Args:
            chunks: List of transcript chunks
            output_dir: Directory to save chunk_vectors.json
            
        Returns:
            List of chunks with embeddings added
        """
        try:
            # Prepare vectors data
            chunk_vectors = []
            
            for i, chunk in enumerate(chunks, 1):
                # Get text from chunk
                text = chunk.get('text', '').strip()
                if not text:
                    logger.warning(f"Empty text in chunk {i}, skipping")
                    continue
                
                # Generate embedding
                vector = self.generate_embedding(text)
                if not vector:
                    logger.warning(f"Failed to generate embedding for chunk {i}")
                    continue
                
                # Create vector entry
                vector_entry = {
                    "chunk_id": f"chunk_{i:03d}",
                    "vector": vector,
                    "text": text
                }
                chunk_vectors.append(vector_entry)
                
                # Add embedding to chunk data
                chunk['embedding'] = vector
            
            # Save vectors to file
            vectors_file = output_dir / "chunk_vectors.json"
            with open(vectors_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "model": self.model.get_sentence_embedding_dimension(),
                    "vectors": chunk_vectors
                }, f, indent=2)
                
            logger.info(f"Saved {len(chunk_vectors)} chunk vectors to {vectors_file}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing chunk vectors: {str(e)}")
            raise
