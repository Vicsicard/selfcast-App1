"""Verify all expected outputs from App 1 processing in both local files and Supabase."""
import os
from pathlib import Path
from typing import Dict, List, Union
import json
import logging

from utils.supabase_client import get_client

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase = get_client()

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
        # Always required
        required_files = [
            "transcript_chunks.md",
            "chunk_metadata.json",
            "video_index.json"
        ]
        
        for file in required_files:
            if not (output_dir / file).exists():
                logger.error(f"Missing required file: {file}")
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

def verify_supabase_outputs(job_id: str, has_video: bool = False, has_audio: bool = False) -> bool:
    """Verify all required files exist in Supabase storage.
    
    Args:
        job_id: The job ID to check files for
        has_video: Whether to check for video files
        has_audio: Whether to check for audio files
        
    Returns:
        bool: True if all required files exist, False otherwise
    """
    required_files = [
        "chunk_metadata.json",
        "transcript_chunks.md",
        "video_index.json"
    ]
    
    try:
        storage_client = supabase.storage()
        
        # Check required files in documents bucket
        try:
            # List files in documents bucket
            response = storage_client.from_("documents").list()
            files = [item["name"] for item in response]
            logger.info(f"Found files in documents: {files}")
            
            # Check each required file exists
            for file in required_files:
                if file not in files:
                    logger.error(f"Missing required file in Supabase: {file}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error listing documents bucket: {str(e)}")
            return False
            
        # Check video files if required
        if has_video:
            try:
                # List files in videos bucket
                response = storage_client.from_("videos").list()
                if not response:
                    logger.error("No files found in video bucket")
                    return False
                    
            except Exception as e:
                logger.error(f"Error listing videos bucket: {str(e)}")
                return False
                
        # Note: Audio files are not uploaded to Supabase in M4A mode
                
        return True
        
    except Exception as e:
        logger.error(f"Error verifying Supabase outputs: {str(e)}")
        return False

def verify_chunk_consistency(file_paths: Dict[str, str], job_info: Dict[str, str]) -> Dict[str, Dict[str, Union[bool, int]]]:
    """Verify that the number of chunks is consistent between local files and Supabase.
    
    Args:
        file_paths: Dictionary of file paths to check
        job_info: Dictionary containing job information
        
    Returns:
        Dictionary containing consistency check results for each file
    """
    results = {}
    
    try:
        # Get local file paths
        output_dir = Path(f"output/job_{job_info['job_id']}/{job_info['job_id']}_{job_info['category']}")
        
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
                        
                # Get Supabase count
                response = supabase.storage.from_("documents").list()
                supabase_count = len([f for f in response if f["name"] == file_name])
                
                results[file_type] = {
                    "consistent": local_count == supabase_count,
                    "local_count": local_count,
                    "supabase_count": supabase_count
                }
                
            except Exception as e:
                logger.error(f"Error checking {file_type}: {str(e)}")
                results[file_type] = {
                    "consistent": False,
                    "local_count": 0,
                    "supabase_count": 0
                }
                
    except Exception as e:
        logger.error(f"Error checking consistency: {str(e)}")
        
    return results

def test_supabase_storage():
    """Test function to verify Supabase storage access."""
    buckets = ["videos", "audio", "documents"]
    
    print("\nVerifying storage access...")
    storage_client = supabase.storage()
    print(f"Storage client type: {type(storage_client)}")
    print(f"Storage client dir: {dir(storage_client)}")
    
    for bucket in buckets:
        try:
            # List files in bucket
            result = storage_client.from_(bucket).list()
            print(f"\n[OK] Can access {bucket}/ bucket")
            
            # Show some example files
            if result:
                print(f"Found {len(result)} files:")
                try:
                    for item in result[:5]:  # Show first 5 files
                        name = str(item['name']) if isinstance(item, dict) else str(item)
                        print(f"  - {name}")
                    if len(result) > 5:
                        print(f"  - ... and {len(result)-5} more")
                except Exception as e:
                    print(f"[WARNING] Could not parse file details: {str(e)}")
                    print(f"Raw result: {result[:5]}")
            else:
                print("  No files found")
                
        except Exception as e:
            print(f"[ERROR] Cannot access {bucket}/ bucket: {str(e)}")
    return True

def main():
    """Run verification of all outputs."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify output files")
    parser.add_argument("--job_id", required=True, help="Job ID to check")
    parser.add_argument("--has_video", action="store_true", help="Check video files")
    parser.add_argument("--has_audio", action="store_true", help="Check audio files")
    args = parser.parse_args()
    
    # Test storage access first
    print("\n[*] Testing storage access...")
    test_supabase_storage()
    
    # Check Supabase outputs
    print("\n[*] Checking Supabase outputs...")
    if not verify_supabase_outputs(args.job_id, args.has_video, args.has_audio):
        print("\n[FAILED] Supabase verification failed")
        return
    print("\n[OK] All required files found in Supabase")

if __name__ == "__main__":
    main()
