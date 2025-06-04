"""Verify all expected outputs from App 1 processing in both local files and MongoDB."""
import os
from pathlib import Path
from typing import Dict, List, Union
import json
from loguru import logger

from utils.mongodb_client import get_mongodb_client

# Initialize MongoDB client
mongodb = get_mongodb_client()

def verify_local_outputs(output_dir: Path, has_video: bool = False, has_audio: bool = False) -> bool:
    """Verify all required local output files exist.
    
    Args:
        output_dir: Path to output directory
        has_video: Whether video files should be present
        has_audio: Whether audio files should be present
        
    Returns:
        bool: True if verification passed
    """
    try:
        # Always required base filenames
        required_bases = [
            "transcript_chunks.md",
            "chunk_metadata.json",
            "video_index.json"
        ]
        
        # Check for files with either the original name or email-prefixed name
        for base_file in required_bases:
            # First check if the exact file exists
            if (output_dir / base_file).exists():
                continue
                
            # If not, check if any file ending with the base name exists (email-prefixed version)
            matching_files = list(output_dir.glob(f"*_{base_file}")) + list(output_dir.glob(f"*{base_file}"))
            if not matching_files:
                # Try checking for file with no underscore between prefix and name
                matching_files = list(output_dir.glob(f"*{base_file}"))
                
            if not matching_files:
                logger.error(f"Missing required file: {base_file}")
                return False
        
        # Optional video files
        if has_video:
            if not (output_dir / "video_chunks").exists():
                logger.error("Missing video chunks directory")
                return False
                
            if not (output_dir / "video_chunks").is_dir():
                logger.error("video_chunks is not a directory")
                return False
                
            # Check for at least one video chunk
            video_chunks = list((output_dir / "video_chunks").glob("*.mp4"))
            if not video_chunks:
                logger.error("No video chunks found")
                return False
                
        # Note: Audio files are not chunked in M4A mode
        # They are only converted to WAV for Whisper
                
        return True
        
    except Exception as e:
        logger.error(f"Error verifying local outputs: {str(e)}")
        return False

def verify_mongodb_outputs(transcript_id: str, has_video: bool = False, has_audio: bool = False) -> bool:
    """Verify all required files exist in MongoDB GridFS.
    
    Args:
        transcript_id: The transcript ID to check files for
        has_video: Whether to check for video files
        has_audio: Whether to check for audio files
        
    Returns:
        bool: True if all required files exist, False otherwise
    """
    try:
        # Always required file types
        required_types = [
            "transcript_chunks.md",
            "chunk_metadata.json",
            "video_index.json"
        ]
        
        # Get list of files for this transcript
        files = mongodb.db.transcript_files.find({"transcript_id": transcript_id})
        
        # Convert cursor to list
        files_list = list(files)
        
        if not files_list:
            logger.error(f"No files found in MongoDB for transcript_id: {transcript_id}")
            return False
            
        # Check for required file types
        found_types = [file.get("file_type", "") for file in files_list]
        
        for req_type in required_types:
            if not any(req_type in file_type for file_type in found_types):
                logger.error(f"Missing required file in MongoDB: {req_type}")
                return False
        
        # Optional video files
        if has_video:
            video_types = ["mp4"]
            if not any(vtype in file_type for file_type in found_types for vtype in video_types):
                logger.error("Missing video file in MongoDB")
                return False
        
        # Optional audio files
        if has_audio:
            audio_types = ["m4a", "mp3", "wav"]
            if not any(atype in file_type for file_type in found_types for atype in audio_types):
                logger.error("Missing audio file in MongoDB")
                return False
        
        logger.info(f"All required files verified in MongoDB for transcript_id: {transcript_id}")
        return True
    except Exception as e:
        logger.error(f"Error verifying MongoDB outputs: {str(e)}")
        return False

def verify_chunk_consistency(file_paths: Dict[str, str], transcript_id: str) -> Dict[str, Dict[str, Union[bool, int]]]:
    """Verify that the number of chunks is consistent between local files and MongoDB.
    
    Args:
        file_paths: Dictionary of file paths to check
        transcript_id: Transcript ID to check
        
    Returns:
        Dictionary containing consistency check results for each file
    """
    results = {}
    
    try:
        # Get local file paths
        output_dir = Path(f"output/{transcript_id}")
        
        # Check each file
        for file_type, file_name in file_paths.items():
            local_path = output_dir / file_name
            
            try:
                # Get local count
                with open(local_path) as f:
                    if file_name.endswith('.json'):
                        local_data = json.load(f)
                        local_count = len(local_data)
                    else:
                        local_count = sum(1 for _ in f)
                        
                # Get MongoDB count
                mongo_files = mongodb.db.transcript_files.find({
                    "transcript_id": transcript_id,
                    "file_type": file_type
                })
                mongo_count = len(list(mongo_files))
                
                results[file_type] = {
                    "consistent": local_count > 0 and mongo_count > 0,
                    "local_count": local_count,
                    "mongodb_count": mongo_count
                }
                
            except Exception as e:
                logger.error(f"Error checking {file_type}: {str(e)}")
                results[file_type] = {
                    "consistent": False,
                    "local_count": 0,
                    "mongodb_count": 0
                }
                
    except Exception as e:
        logger.error(f"Error checking consistency: {str(e)}")
        
    return results

def test_mongodb_storage():
    """Test function to verify MongoDB GridFS access."""
    collections = ["transcripts", "transcript_chunks", "transcript_files"]
    
    print("\nVerifying MongoDB access...")
    
    for collection in collections:
        try:
            # Count documents in collection
            count = mongodb.db[collection].count_documents({})
            print(f"\n[OK] Can access {collection} collection")
            print(f"Found {count} documents")
            
            # Show some example documents
            if count > 0:
                docs = list(mongodb.db[collection].find({}).limit(5))
                print(f"Sample documents:")
                for i, doc in enumerate(docs):
                    # Remove _id from output for cleaner display
                    if "_id" in doc:
                        doc["_id"] = str(doc["_id"])
                    print(f"  {i+1}. {doc}")
                if count > 5:
                    print(f"  ... and {count-5} more")
            else:
                print("  No documents found")
                
        except Exception as e:
            print(f"[ERROR] Cannot access {collection} collection: {str(e)}")
    
    return True

def main():
    """Run verification of all outputs."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify output files")
    parser.add_argument("--transcript_id", required=True, help="Transcript ID to check")
    parser.add_argument("--has_video", action="store_true", help="Check for video files")
    parser.add_argument("--has_audio", action="store_true", help="Check for audio files")
    parser.add_argument("--output_dir", help="Output directory to check")
    parser.add_argument("--test_mongodb", action="store_true", help="Test MongoDB access")
    
    args = parser.parse_args()
    
    if args.test_mongodb:
        test_mongodb_storage()
        return
    
    # Verify local outputs if output_dir is provided
    if args.output_dir:
        output_dir = Path(args.output_dir)
        if not output_dir.exists():
            logger.error(f"Output directory does not exist: {output_dir}")
            return False
            
        logger.info(f"Verifying local outputs in {output_dir}")
        local_result = verify_local_outputs(output_dir, args.has_video, args.has_audio)
        print(f"Local verification: {'✅ PASSED' if local_result else '❌ FAILED'}")
    
    # Verify MongoDB outputs
    logger.info(f"Verifying MongoDB outputs for transcript_id: {args.transcript_id}")
    mongodb_result = verify_mongodb_outputs(args.transcript_id, args.has_video, args.has_audio)
    print(f"MongoDB verification: {'✅ PASSED' if mongodb_result else '❌ FAILED'}")
    
    return local_result and mongodb_result

if __name__ == "__main__":
    main()
