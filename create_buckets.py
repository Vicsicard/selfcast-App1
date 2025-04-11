import requests
import json

# Supabase configuration
SUPABASE_URL = "https://aqicztygjpmunfljjuto.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxaWN6dHlnanBtdW5mbGpqdXRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzcwNTU4MiwiZXhwIjoyMDU5MjgxNTgyfQ.lIfnbWUDm8yDz1g_gQJNi56rCiGRAunY48rgVAwLID4"

# Headers for API requests
headers = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json"
}

# Required bucket names
BUCKETS = ["videos", "audio", "documents"]

def create_bucket(name):
    url = f"{SUPABASE_URL}/storage/v1/bucket"
    data = {
        "id": name,
        "name": name,
        "public": False,
        "file_size_limit": 52428800,  # 50MB limit
        "allowed_mime_types": ["*/*"]  # Allow all file types
    }
    
    # First check if bucket exists
    check_url = f"{SUPABASE_URL}/storage/v1/bucket/{name}"
    check_response = requests.get(check_url, headers=headers)
    
    if check_response.status_code == 200:
        print(f"[OK] Bucket '{name}' already exists")
        return True
        
    # Create bucket if it doesn't exist
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"[OK] Created bucket '{name}'")
        return True
    else:
        print(f"[ERROR] Failed to create bucket '{name}': {response.text}")
        return False

def update_bucket_policy(name):
    """Update bucket policy to allow authenticated users to read."""
    url = f"{SUPABASE_URL}/storage/v1/bucket/{name}/policy"
    
    # Policy for authenticated users to read files
    read_policy = {
        "name": f"authenticated can read {name}",
        "definition": {
            "role": "authenticated",
            "operations": ["select"]
        }
    }
    
    response = requests.put(url, headers=headers, json=read_policy)
    if response.status_code in [200, 201]:
        print(f"[OK] Updated read policy for '{name}'")
        return True
    else:
        print(f"[ERROR] Failed to update policy for '{name}': {response.text}")
        return False

print("\nChecking and creating buckets...")
for bucket in BUCKETS:
    if create_bucket(bucket):
        update_bucket_policy(bucket)
    print()
