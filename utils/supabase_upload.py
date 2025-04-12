"""Utility functions for uploading files to Supabase Storage."""
import os
from pathlib import Path
from typing import Optional
from supabase import create_client, Client
import uuid
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
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file_to_supabase(
    bucket: str,
    file_path: str,
    file_type: str,
    file_name: Optional[str] = None
) -> str:
    """Upload a file to Supabase Storage.
    
    Args:
        bucket: Name of the storage bucket (videos, audio, documents)
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
    storage_path = file_name
    
    try:
        # Check if file exists
        try:
            supabase.storage.from_(bucket).download(storage_path)
            exists = True
        except:
            exists = False
            
        # Upload or update file
        with open(file_path, "rb") as f:
            if exists:
                # Update existing file
                result = supabase.storage.from_(bucket).update(
                    path=storage_path,
                    file=f,
                    file_options={"content-type": "application/octet-stream"}
                )
                print(f"[OK] Updated {file_name} in {bucket}/{storage_path}")
            else:
                # Upload new file
                result = supabase.storage.from_(bucket).upload(
                    path=storage_path,
                    file=f,
                    file_options={"content-type": "application/octet-stream"}
                )
                print(f"[OK] Uploaded {file_name} to {bucket}/{storage_path}")
            
        # Get public URL
        file_url = supabase.storage.from_(bucket).get_public_url(storage_path)
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
    
    try:
        # Upload metadata files
        metadata_files = {
            "transcript_chunks.md": "text/markdown",
            "chunk_vectors.json": "application/json",
            "video_index.json": "application/json",
            "chunk_metadata.json": "application/json"
        }
        for metadata_file, mime_type in metadata_files.items():
            upload_file_to_supabase(
                bucket="documents",
                file_path=os.path.join(input_dir, metadata_file),
                file_type=mime_type
            )
            
        print("\nAll files uploaded successfully!")
                
    except Exception as e:
        print(f"\nError during upload: {str(e)}")
        raise
