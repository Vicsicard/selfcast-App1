"""Test environment variable loading."""
from dotenv import load_dotenv
import os
from loguru import logger

def test_supabase_env():
    """Test if Supabase environment variables are loaded correctly."""
    # Load environment variables
    load_dotenv()
    
    # Check required variables
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_PROJECT_ID',
        'SUPABASE_ANON_KEY'
    ]
    
    success = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✓ {var} is set")
            # Show first/last few chars of value for verification
            preview = f"{value[:8]}...{value[-8:]}" if len(value) > 20 else value
            logger.info(f"  Value: {preview}")
        else:
            logger.error(f"✗ {var} is not set!")
            success = False
    
    return success

if __name__ == "__main__":
    success = test_supabase_env()
    if success:
        logger.info("All required environment variables are set correctly!")
    else:
        logger.error("Some environment variables are missing!")
