import requests
import json

# Supabase configuration
SUPABASE_URL = "https://aqicztygjpmunfljjuto.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxaWN6dHlnanBtdW5mbGpqdXRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzcwNTU4MiwiZXhwIjoyMDU5MjgxNTgyfQ.lIfnbWUDm8yDz1g_gQJNi56rCiGRAunY48rgVAwLID4"

# Headers for API requests
headers = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def setup_database():
    """Set up the required database tables and schema."""
    
    # Create transcript_files table
    create_table_sql = """
    create table if not exists transcript_files (
        id uuid default uuid_generate_v4() primary key,
        user_id text not null,
        transcript_id text not null,
        file_type text not null,
        file_name text not null,
        file_path text not null,
        bucket text not null,
        status text default 'uploaded',
        chunk_count integer,
        linked_project_id text,
        client_email text,
        content_type text,
        description text,
        created_at timestamptz default now(),
        updated_at timestamptz default now()
    );
    
    -- Add indexes for better query performance
    create index if not exists idx_transcript_files_user_id on transcript_files(user_id);
    create index if not exists idx_transcript_files_transcript_id on transcript_files(transcript_id);
    """
    
    # Execute SQL using the REST API
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    data = {"sql_query": create_table_sql}
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("[OK] Created transcript_files table and indexes")
    else:
        print(f"[ERROR] Failed to create table: {response.text}")
        return False
    
    return True

if __name__ == "__main__":
    if setup_database():
        print("\nDatabase setup completed successfully")
    else:
        print("\nDatabase setup failed")
