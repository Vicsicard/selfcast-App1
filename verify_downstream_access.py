"""Verify downstream access requirements for uploaded files."""
import requests
import json
from datetime import datetime

# Supabase configuration
SUPABASE_URL = "https://aqicztygjpmunfljjuto.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxaWN6dHlnanBtdW5mbGpqdXRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzcwNTU4MiwiZXhwIjoyMDU5MjgxNTgyfQ.lIfnbWUDm8yDz1g_gQJNi56rCiGRAunY48rgVAwLID4"

# Headers for API requests
headers = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY
}

def check_bucket_access(bucket: str, required_files: list = None):
    """Check if a bucket exists and contains required files."""
    # First check bucket existence
    bucket_url = f"{SUPABASE_URL}/storage/v1/bucket/{bucket}"
    response = requests.get(bucket_url, headers=headers)
    
    if response.status_code != 200:
        print(f"[ERROR] Cannot access {bucket}/ bucket")
        return False, []
        
    # Then list files
    list_url = f"{SUPABASE_URL}/storage/v1/object/list/{bucket}"
    response = requests.get(list_url, headers=headers)
    
    if response.status_code != 200:
        print(f"[ERROR] Cannot list files in {bucket}/ bucket")
        return False, []
        
    files = response.json()
    print(f"[OK] Can access {bucket}/ bucket ({len(files)} files)")
    
    if required_files:
        missing = []
        for file in required_files:
            if not any(f['name'] == file for f in files):
                missing.append(file)
                
        if missing:
            print(f"[ERROR] Missing required files in {bucket}/: {', '.join(missing)}")
            return False, files
    
    return True, files

def verify_app2_requirements():
    """Verify App 2 requirements (documents/ access)"""
    print("\nVerifying App 2 Requirements:")
    required_files = ['transcript_chunks.md']
    success, files = check_bucket_access('documents', required_files)
    if success:
        print("[OK] App 2 can access required files")
        for f in files:
            print(f"  - {f['name']} ({f['metadata'].get('mimetype', 'unknown type')})")
    return success

def verify_app4_requirements():
    """Verify App 4 requirements (video_index.json + videos/)"""
    print("\nVerifying App 4 Requirements:")
    
    # Check video_index.json
    success1, doc_files = check_bucket_access('documents', ['video_index.json'])
    if success1:
        for f in doc_files:
            if f['name'] == 'video_index.json':
                print(f"  - Found {f['name']} ({f['metadata'].get('mimetype', 'unknown type')})")
    
    # Check videos bucket
    success2, video_files = check_bucket_access('videos')
    if success2:
        print(f"  - Found {len(video_files)} video chunks")
        for f in video_files[:3]:  # Show first 3 as example
            print(f"  - {f['name']} ({f['metadata'].get('mimetype', 'unknown type')})")
        if len(video_files) > 3:
            print(f"  - ... and {len(video_files)-3} more")
    
    if success1 and success2:
        print("[OK] App 4 can access required files")
    return success1 and success2

def verify_client_dashboard():
    """Verify client dashboard can see transcript status"""
    print("\nVerifying Client Dashboard Access:")
    
    url = f"{SUPABASE_URL}/rest/v1/transcript_files"
    response = requests.get(url, headers={**headers, "Content-Type": "application/json"})
    
    if response.status_code != 200:
        print("[ERROR] Cannot access transcript_files table")
        return False
        
    entries = response.json()
    if not entries:
        print("[ERROR] No entries found in transcript_files table")
        return False
        
    print(f"[OK] Found {len(entries)} entries in transcript_files table")
    
    # Group files by user_id since that's what we have
    users = {}
    for entry in entries:
        uid = entry.get('user_id', 'unknown')
        if uid not in users:
            users[uid] = {'files': []}
        users[uid]['files'].append(entry.get('file_name', 'unknown'))
    
    print(f"[OK] Found {len(users)} unique users")
    for uid, data in users.items():
        print(f"  - User {uid}: {len(data['files'])} files")
    
    return True

if __name__ == "__main__":
    print("Verifying downstream access requirements...")
    
    app2_ok = verify_app2_requirements()
    app4_ok = verify_app4_requirements()
    dashboard_ok = verify_client_dashboard()
    
    print("\nSummary:")
    if app2_ok:
        print("[PASS] App 2 can read from documents/")
    else:
        print("[FAIL] App 2 may have issues accessing documents/")
        
    if app4_ok:
        print("[PASS] App 4 can use video_index.json + videos/")
    else:
        print("[FAIL] App 4 may have issues with video files")
        
    if dashboard_ok:
        print("[PASS] Client dashboard can access transcript status")
    else:
        print("[FAIL] Client dashboard may have issues viewing status")
