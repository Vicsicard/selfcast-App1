import requests

# Supabase configuration
SUPABASE_URL = "https://aqicztygjpmunfljjuto.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxaWN6dHlnanBtdW5mbGpqdXRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzcwNTU4MiwiZXhwIjoyMDU5MjgxNTgyfQ.lIfnbWUDm8yDz1g_gQJNi56rCiGRAunY48rgVAwLID4"

# Headers for API requests
headers = {
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

def list_files(bucket, path):
    url = f"{SUPABASE_URL}/storage/v1/object/list/{bucket}/{path}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        files = response.json()
        print(f"\n[{bucket}] Files in {path}:")
        for file in files:
            print(f"- {file['name']} ({file['metadata']['size']} bytes)")
    else:
        print(f"[ERROR] Failed to list files in {bucket}/{path}: {response.text}")

# Check each bucket
list_files("videos", "20250411_141510_interview")
list_files("audio", "20250411_141510_interview")
list_files("documents", "20250411_141510_interview")
