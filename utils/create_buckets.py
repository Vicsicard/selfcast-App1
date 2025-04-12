"""Create required storage buckets in Supabase."""
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing Supabase credentials. Ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in your environment."
    )

# Initialize Supabase client with service role key for admin operations
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_bucket(name: str):
    """Create a storage bucket if it doesn't exist."""
    try:
        # Create bucket (will fail if it already exists)
        supabase.storage.create_bucket(id=name, options={"public": True})
        print(f"[OK] Created bucket: {name}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"[OK] Bucket already exists: {name}")
        else:
            print(f"[ERROR] Failed to create bucket {name}: {str(e)}")

def main():
    """Create all required buckets."""
    required_buckets = ["documents", "audio", "videos"]
    for bucket in required_buckets:
        create_bucket(bucket)

if __name__ == "__main__":
    main()
