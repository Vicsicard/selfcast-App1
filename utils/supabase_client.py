"""Centralized Supabase client for server-side operations."""
import os
from typing import Optional
from supabase import create_client, Client
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global client instance
_supabase_client: Optional[Client] = None

def get_client() -> Client:
    """Get or create a Supabase client instance.
    
    Returns:
        Client: Supabase client instance
    
    Raises:
        ValueError: If required environment variables are missing
    """
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
        
    # Get credentials from environment
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError(
            "Missing Supabase credentials. Ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set."
        )
    
    try:
        # Create client with minimal config
        _supabase_client = create_client(
            supabase_url=SUPABASE_URL,
            supabase_key=SUPABASE_SERVICE_KEY
        )
        logger.info("Supabase client initialized successfully")
        return _supabase_client
        
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        raise
