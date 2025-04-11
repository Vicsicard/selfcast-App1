"""Utility functions for uploading files to Supabase Storage."""
import os
from pathlib import Path
from typing import Optional
from supabase import create_client, Client
import uuid

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing Supabase credentials. Ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in your environment."
    )

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file_to_supabase(
    bucket: str,
    user_id: str,
    transcript_id: str,
    file_path: str,
    file_type: str,
    file_name: Optional[str] = None
) -> str:
    """Upload a file to Supabase Storage and record its metadata.
    
    Args:
        bucket: Name of the storage bucket (videos, audio, documents)
        user_id: UUID of the user
        transcript_id: UUID of the transcript
        file_path: Path to the file to upload
        file_type: Type of file (video, audio, transcript, metadata)
        file_name: Optional custom file name, defaults to original name
    
    Returns:
        str: URL of the uploaded file
    
    Raises:
        Exception: If upload fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    # Use original filename if none provided
    if not file_name:
        file_name = Path(file_path).name
        
    # Generate storage path
    storage_path = f"{transcript_id}/{file_name}"
    
    try:
        # Upload file to storage
        with open(file_path, "rb") as f:
            result = supabase.storage.from_(bucket).upload(
                path=storage_path,
                file=f,
                file_options={"content-type": "application/octet-stream"}
            )
            
        # Get public URL
        file_url = supabase.storage.from_(bucket).get_public_url(storage_path)
            
        # Record file metadata
        data = {
            "user_id": user_id,
            "transcript_id": transcript_id,
            "file_type": file_type,
            "file_name": file_name,
            "file_path": storage_path,
            "bucket": bucket
        }
            
        result = supabase.table("transcript_files").insert(data).execute()
        
        print(f"[OK] Uploaded {file_name} to {bucket}/{storage_path}")
        return file_url
            
    except Exception as e:
        print(f"[ERROR] Failed to upload {file_name}: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload files to Supabase Storage")
    parser.add_argument("--input-dir", required=True, help="Input directory containing files to upload")
    parser.add_argument("--category", required=True, help="Category for the files")
    args = parser.parse_args()
    
    input_dir = args.input_dir
    category = args.category
    
    # Generate IDs
    user_id = "test_user"  # TODO: Get from auth
    transcript_id = str(uuid.uuid4())
    
    try:
        # Upload video chunks
        video_dir = os.path.join(input_dir, "video_chunks")
        video_files = sorted([f for f in os.listdir(video_dir) if f.endswith('.mp4')])
        for video_file in video_files:
            upload_file_to_supabase(
                bucket="videos",
                user_id=user_id,
                transcript_id=transcript_id,
                file_path=os.path.join(video_dir, video_file),
                file_type="video/mp4"
            )
            
        # Upload audio chunks
        audio_dir = os.path.join(input_dir, "audio_chunks")
        audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.m4a')])
        for audio_file in audio_files:
            upload_file_to_supabase(
                bucket="audio",
                user_id=user_id,
                transcript_id=transcript_id,
                file_path=os.path.join(audio_dir, audio_file),
                file_type="audio/m4a"
            )
            
        # Upload metadata files
        metadata_files = {
            "transcript_chunks.md": "text/markdown",
            "chunk_vectors.json": "application/json",
            "video_index.json": "application/json"
        }
        for metadata_file, mime_type in metadata_files.items():
            upload_file_to_supabase(
                bucket="documents",
                user_id=user_id,
                transcript_id=transcript_id,
                file_path=os.path.join(input_dir, metadata_file),
                file_type=mime_type
            )
            
        # Verify all uploads
        expected_files = {
            "videos": [f"chunk_{i:03d}.mp4" for i in range(1, len(video_files) + 1)],
            "audio": [f"chunk_{i:03d}.m4a" for i in range(1, len(audio_files) + 1)],
            "documents": list(metadata_files.keys())
        }
        
        if verify_uploads(expected_files):
            print("\n✅ All files uploaded and verified successfully!")
        else:
            print("\n❌ Some files are missing or failed to upload")
            
    except Exception as e:
        print(f"\nError during upload: {str(e)}")
        raise
