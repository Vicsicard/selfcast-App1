"""Utility functions for uploading files to Supabase Storage."""
import os
from typing import Union, Optional
from datetime import datetime
from loguru import logger
from .supabase_client import get_client

def upload_file_to_supabase(
    bucket: str,
    user_id: str,
    transcript_id: str,
    file_path: str,
    file_type: str,  # e.g. 'video', 'chunked_video', 'transcript', 'metadata'
    file_name: Optional[str] = None
) -> str:
    """Upload a file to Supabase Storage and log its metadata in the transcript_files table.
    
    Args:
        bucket: The Supabase storage bucket name
        user_id: The ID of the user who owns this file
        transcript_id: The ID of the transcript this file belongs to
        file_path: Path to the file to upload
        file_type: Type of file being uploaded
        file_name: Optional custom name for the file in storage. If not provided,
                  uses the original file name.
        
    Returns:
        str: The storage path where the file was uploaded
        
    Raises:
        Exception: If upload or database logging fails
    """
    supabase = get_client()
    
    # Generate storage path
    if file_name is None:
        file_name = os.path.basename(file_path)
    storage_path = f"{user_id}/{transcript_id}/{file_name}"
    
    # Upload file
    with open(file_path, 'rb') as f:
        result = supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=f,
            file_options={"upsert": True}
        )
        if hasattr(result, 'error') and result.error:
            raise Exception(f"Upload failed: {result.error}")
    
    # Log file metadata in database
    data = {
        "user_id": user_id,
        "transcript_id": transcript_id,
        "file_type": file_type,
        "file_name": file_name,
        "file_path": storage_path,
        "bucket": bucket,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("transcript_files").insert(data).execute()
    if hasattr(result, 'error') and result.error:
        raise Exception(f"DB logging failed: {result.error}")
        
    return storage_path
