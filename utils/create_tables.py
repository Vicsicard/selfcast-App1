"""Create required database tables in Supabase."""
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

def create_transcript_files_table():
    """Create the transcript_files table if it doesn't exist."""
    try:
        # Create table using raw SQL
        sql = """
        CREATE TABLE IF NOT EXISTS transcript_files (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id TEXT NOT NULL,
            transcript_id TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            bucket TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
        );
        """
        supabase.table("transcript_files").select("*").limit(1).execute()
        print("[OK] transcript_files table already exists")
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            try:
                result = supabase.query(sql).execute()
                print("[OK] Created transcript_files table")
            except Exception as e2:
                print(f"[ERROR] Failed to create transcript_files table: {str(e2)}")
        else:
            print(f"[ERROR] Unexpected error: {str(e)}")

def main():
    """Create all required tables."""
    create_transcript_files_table()

if __name__ == "__main__":
    main()
