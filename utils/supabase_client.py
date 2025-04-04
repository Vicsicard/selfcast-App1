"""
Supabase Client Module

Provides a centralized Supabase client instance for use across the application.
Uses environment variables for configuration:
- SUPABASE_URL: Your Supabase project URL
- SUPABASE_SERVICE_ROLE_KEY: Your Supabase service role key (for server-side operations)
"""

import os
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from loguru import logger

# Load environment variables
load_dotenv()

# Get Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Using service role key for server-side operations

# Initialize Supabase client
supabase: Optional[Client] = None

def get_client() -> Client:
    """
    Get the Supabase client instance. Creates a new instance if none exists.
    
    Returns:
        Client: Initialized Supabase client
        
    Raises:
        ValueError: If required environment variables are not set
    """
    global supabase
    
    if supabase is not None:
        return supabase
        
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError(
            "Supabase configuration missing. Please set SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY environment variables."
        )
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("Supabase client initialized successfully")
        return supabase
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        raise
