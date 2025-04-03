"""
Similarity calculation utilities using scikit-learn.
"""
from typing import List, Tuple
import numpy as np
from sklearn.preprocessing import normalize
from typing import Optional

def normalize_vector(vector: List[float]) -> np.ndarray:
    """
    Normalize a vector to unit length.
    
    Args:
        vector: Input vector
        
    Returns:
        Normalized vector as numpy array
    """
    if not vector:
        return np.array([])
    vec_array = np.array(vector).reshape(1, -1)
    return normalize(vec_array, norm='l2')[0]

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors with proper normalization.
    
    Args:
        v1: First vector
        v2: Second vector
        
    Returns:
        Cosine similarity score
    """
    if not v1 or not v2:
        return 0.0
        
    try:
        # Normalize both vectors
        v1_norm = normalize_vector(v1)
        v2_norm = normalize_vector(v2)
        
        # Calculate cosine similarity
        return float(np.dot(v1_norm, v2_norm))
    except Exception as e:
        print(f"Error calculating similarity: {str(e)}")
        return 0.0

def find_best_match(
    query_embedding: List[float],
    reference_embeddings: List[List[float]],
    threshold: float = 0.80
) -> Tuple[int, float]:
    """
    Find best matching reference embedding above threshold.
    
    Args:
        query_embedding: Query vector
        reference_embeddings: List of reference vectors
        threshold: Minimum similarity score (default: 0.80)
        
    Returns:
        Tuple of (best match index, similarity score)
        Returns (-1, 0.0) if no match above threshold is found
    """
    if not query_embedding or not reference_embeddings:
        return -1, 0.0
    
    # Normalize query vector once
    query_norm = normalize_vector(query_embedding)
    
    # Calculate similarities with all reference embeddings
    similarities = []
    for ref_embedding in reference_embeddings:
        ref_norm = normalize_vector(ref_embedding)
        score = float(np.dot(query_norm, ref_norm))
        similarities.append(score)
    
    # Find best match above threshold
    max_score = max(similarities) if similarities else 0.0
    if max_score >= threshold:
        best_idx = similarities.index(max_score)
        return best_idx, max_score
        
    return -1, 0.0
