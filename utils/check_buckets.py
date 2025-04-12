"""Check contents of Supabase storage buckets."""
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

def list_files(bucket_name: str):
    """List all files in a bucket."""
    print(f"\n[*] Listing contents of {bucket_name} bucket:")
    try:
        res = supabase.storage.from_(bucket_name).list()
        for item in res:
            print(f"- {item['name']}")
    except Exception as e:
        print(f"[ERROR] Failed to list bucket {bucket_name}: {str(e)}")

def main():
    """Check all buckets."""
    buckets = ["documents", "audio", "videos"]
    for bucket in buckets:
        list_files(bucket)

if __name__ == "__main__":
    main()
