#!/usr/bin/env python
"""
MongoDB Upload Utility - Handles file uploads to MongoDB GridFS
Replaces Supabase storage with MongoDB for transcript processing
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger
import gridfs
import mimetypes

from utils.mongodb_client import get_mongodb_client

def upload_file_to_mongodb(
    file_path: str,
    file_type: str,
    metadata: Optional[Dict[str, Any]] = None,
    transcript_id: Optional[str] = None,
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    file_name: Optional[str] = None
) -> str:
    """Upload a file to MongoDB GridFS.
    
    Args:
        file_path: Path to the file to upload
        file_type: Type of file (video, audio, transcript, metadata)
        metadata: Optional metadata about the file
        transcript_id: Optional ID of associated transcript
        user_id: Optional ID of user who owns the file
        category: Optional category for organizing files
        file_name: Optional custom file name, defaults to original name
    
    Returns:
        str: MongoDB ID of uploaded file
    
    Raises:
        Exception: If upload fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    # Use original filename if none provided
    if not file_name:
        file_name = Path(file_path).name
    
    # Get MongoDB client
    mongodb = get_mongodb_client()
    if not mongodb.db:
        raise ConnectionError("MongoDB connection not available")
    
    # Create GridFS instance
    fs = gridfs.GridFS(mongodb.db)
    
    try:
        # Prepare metadata
        file_metadata = metadata or {}
        file_metadata.update({
            'filename': file_name,
            'file_type': file_type,
            'content_type': mimetypes.guess_type(file_path)[0] or 'application/octet-stream',
            'uploaded_at': datetime.now().isoformat(),
            'file_size': os.path.getsize(file_path)
        })
        
        if transcript_id:
            file_metadata['transcript_id'] = transcript_id
            
        if user_id:
            file_metadata['user_id'] = user_id
            
        if category:
            file_metadata['category'] = category
        
        # Upload file to GridFS
        with open(file_path, 'rb') as f:
            file_id = fs.put(f, **file_metadata)
        
        file_id_str = str(file_id)
        logger.info(f"Uploaded {file_name} to MongoDB GridFS with ID: {file_id_str}")
        
        # Log file metadata in transcript_files collection
        mongodb.db.transcript_files.insert_one({
            'file_id': file_id_str,
            'filename': file_name,
            'file_type': file_type,
            'content_type': file_metadata['content_type'],
            'file_size': file_metadata['file_size'],
            'transcript_id': transcript_id,
            'user_id': user_id,
            'category': category,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })
        
        return file_id_str
            
    except Exception as e:
        logger.error(f"Failed to upload {file_name} to MongoDB: {str(e)}")
        raise

def download_file_from_mongodb(
    file_id: str,
    output_path: str
) -> bool:
    """Download a file from MongoDB GridFS.
    
    Args:
        file_id: MongoDB ID of file
        output_path: Path to save downloaded file
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Get MongoDB client
    mongodb = get_mongodb_client()
    if not mongodb.db:
        logger.error("MongoDB connection not available")
        return False
    
    # Create GridFS instance
    fs = gridfs.GridFS(mongodb.db)
    
    try:
        # Check if file exists
        if not fs.exists(file_id):
            logger.error(f"File {file_id} not found in MongoDB GridFS")
            return False
        
        # Download file
        with fs.get(file_id) as f:
            with open(output_path, 'wb') as out:
                out.write(f.read())
        
        logger.info(f"Downloaded file {file_id} to {output_path}")
        return True
            
    except Exception as e:
        logger.error(f"Failed to download file {file_id}: {str(e)}")
        return False

def list_files_in_mongodb(
    transcript_id: Optional[str] = None,
    user_id: Optional[str] = None,
    file_type: Optional[str] = None
) -> list:
    """List files in MongoDB GridFS.
    
    Args:
        transcript_id: Optional ID of associated transcript
        user_id: Optional ID of user who owns the files
        file_type: Optional type of files to list
    
    Returns:
        list: List of file metadata
    """
    # Get MongoDB client
    mongodb = get_mongodb_client()
    if not mongodb.db:
        logger.error("MongoDB connection not available")
        return []
    
    try:
        # Build query
        query = {}
        if transcript_id:
            query['transcript_id'] = transcript_id
        if user_id:
            query['user_id'] = user_id
        if file_type:
            query['file_type'] = file_type
        
        # Query transcript_files collection
        files = list(mongodb.db.transcript_files.find(query))
        
        # Convert ObjectId to string for JSON serialization
        for file in files:
            if '_id' in file:
                file['_id'] = str(file['_id'])
        
        return files
            
    except Exception as e:
        logger.error(f"Failed to list files in MongoDB: {str(e)}")
        return []

def delete_file_from_mongodb(file_id: str) -> bool:
    """Delete a file from MongoDB GridFS.
    
    Args:
        file_id: MongoDB ID of file
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Get MongoDB client
    mongodb = get_mongodb_client()
    if not mongodb.db:
        logger.error("MongoDB connection not available")
        return False
    
    # Create GridFS instance
    fs = gridfs.GridFS(mongodb.db)
    
    try:
        # Check if file exists
        if not fs.exists(file_id):
            logger.error(f"File {file_id} not found in MongoDB GridFS")
            return False
        
        # Delete file from GridFS
        fs.delete(file_id)
        
        # Delete file metadata from transcript_files collection
        mongodb.db.transcript_files.delete_one({'file_id': str(file_id)})
        
        logger.info(f"Deleted file {file_id} from MongoDB")
        return True
            
    except Exception as e:
        logger.error(f"Failed to delete file {file_id}: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload files to MongoDB GridFS")
    parser.add_argument("--input-dir", required=True, help="Input directory containing files to upload")
    parser.add_argument("--category", required=True, help="Category for the files")
    parser.add_argument("--transcript-id", help="ID of associated transcript")
    parser.add_argument("--user-id", help="ID of user who owns the files")
    args = parser.parse_args()
    
    input_dir = args.input_dir
    category = args.category
    transcript_id = args.transcript_id
    user_id = args.user_id
    
    try:
        # Upload metadata files
        metadata_files = {
            "transcript_chunks.md": "text/markdown",
            "chunk_vectors.json": "application/json",
            "video_index.json": "application/json",
            "chunk_metadata.json": "application/json"
        }
        for metadata_file, mime_type in metadata_files.items():
            file_path = os.path.join(input_dir, metadata_file)
            if os.path.exists(file_path):
                upload_file_to_mongodb(
                    file_path=file_path,
                    file_type=mime_type,
                    transcript_id=transcript_id,
                    user_id=user_id,
                    category=category
                )
            
        print("\nAll files uploaded successfully!")
                
    except Exception as e:
        print(f"\nError during upload: {str(e)}")
        raise
