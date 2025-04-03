"""Test Supabase connection and chunks table."""
from dotenv import load_dotenv
import os
from supabase import create_client
from loguru import logger
import numpy as np
from sentence_transformers import SentenceTransformer

def test_supabase_connection():
    """Test connecting to Supabase and basic table operations."""
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    try:
        # Initialize Supabase client
        logger.info("Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by inserting a test chunk
        logger.info("Testing chunks table with a sample insert...")
        
        # Generate a test embedding
        model = SentenceTransformer('all-MiniLM-L6-v2')
        test_text = "This is a test response"
        embedding = model.encode(test_text, convert_to_tensor=False).tolist()
        
        # Create test data
        test_chunk = {
            "chunk_id": "test_chunk_001",
            "question_id": "test_q_001",
            "question_text": "Is this a test?",
            "response_text": test_text,
            "start_time": "00:00",
            "end_time": "00:05",
            "similarity_score": 0.95,
            "vector_embedding": embedding,
            "project_id": "test_project",
            "user_id": "test_user"
        }
        
        # Insert test chunk
        result = supabase.table("chunks").insert(test_chunk).execute()
        
        # Verify the insert
        if result.data:
            logger.info("✓ Successfully inserted test chunk")
            
            # Clean up test data
            logger.info("Cleaning up test data...")
            supabase.table("chunks").delete().eq("chunk_id", "test_chunk_001").execute()
            logger.info("✓ Test data cleaned up")
            
            return True
        else:
            logger.error("Failed to insert test chunk")
            return False
            
    except Exception as e:
        logger.error(f"Error testing Supabase connection: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    if success:
        logger.info("All Supabase connection tests passed!")
    else:
        logger.error("Supabase connection test failed!")
