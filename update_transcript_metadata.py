import requests
import json
import os
from datetime import datetime

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

def update_transcript_metadata(transcript_id: str, input_dir: str):
    """Update transcript metadata in the transcript_files table."""
    
    # Count video chunks to get chunk_count
    video_dir = os.path.join(input_dir, "video_chunks")
    chunk_count = len([f for f in os.listdir(video_dir) if f.endswith('.mp4')])
    
    # Prepare update data
    update_data = {
        "status": "complete",
        "chunk_count": chunk_count,
        "updated_at": datetime.utcnow().isoformat(),
        "linked_project_id": "interview_" + transcript_id,  # Using transcript_id as project ID
        "client_email": "annie.sicard@example.com"  # Example client email
    }
    
    # Update all files for this transcript
    url = f"{SUPABASE_URL}/rest/v1/transcript_files"
    query_params = {"transcript_id": f"eq.{transcript_id}"}
    
    # First, get current entries
    response = requests.get(url, headers=headers, params=query_params)
    if response.status_code != 200:
        print(f"Failed to get transcript files: {response.text}")
        return False
        
    entries = response.json()
    if not entries:
        print(f"No entries found for transcript_id: {transcript_id}")
        return False
        
    # Update each entry
    success = True
    for entry in entries:
        entry_id = entry['id']
        
        # Add file-specific metadata
        file_data = update_data.copy()
        if entry['file_name'] == 'transcript_chunks.md':
            file_data.update({
                "content_type": "text/markdown",
                "description": "Main transcript content with 222 chunks"
            })
        elif entry['file_name'] == 'video_index.json':
            file_data.update({
                "content_type": "application/json",
                "description": "Video segment index and metadata"
            })
        elif entry['file_name'] == 'chunk_vectors.json':
            file_data.update({
                "content_type": "application/json",
                "description": "Embeddings for transcript chunks"
            })
        elif entry['file_name'].endswith('.mp4'):
            file_data.update({
                "content_type": "video/mp4",
                "description": f"Video chunk {entry['file_name']}"
            })
        elif entry['file_name'].endswith('.m4a'):
            file_data.update({
                "content_type": "audio/m4a",
                "description": f"Audio chunk {entry['file_name']}"
            })
            
        # Update entry
        update_url = f"{url}?id=eq.{entry_id}"
        response = requests.patch(update_url, headers=headers, json=file_data)
        
        if response.status_code == 200:
            print(f"✓ Updated metadata for {entry['file_name']}")
        else:
            print(f"✗ Failed to update {entry['file_name']}: {response.text}")
            success = False
            
    return success

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update transcript metadata")
    parser.add_argument("--transcript-id", required=True, help="Transcript ID to update")
    parser.add_argument("--input-dir", required=True, help="Input directory with processed files")
    args = parser.parse_args()
    
    if update_transcript_metadata(args.transcript_id, args.input_dir):
        print("\n✅ Successfully updated transcript metadata")
    else:
        print("\n❌ Failed to update some metadata entries")
