"""
CLI tool to process interview videos into transcript chunks and video segments.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any
from loguru import logger

from utils.video_segmenter import VideoSegmenter

def setup_directories(base_dir: Path) -> Dict[str, Path]:
    """Create required directories if they don't exist."""
    dirs = {
        'video_chunks': base_dir / 'video_chunks',
        'transcripts': base_dir / 'transcripts'
    }
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    return dirs

def process_interview(
    input_video: Path,
    metadata_path: Path,
    output_dir: Path,
    error_log: Path = Path('errors.log')
) -> bool:
    """
    Process an interview video:
    1. Load chunk metadata
    2. Export video segments
    3. Create video index
    """
    try:
        # Initialize video segmenter
        segmenter = VideoSegmenter(metadata_path)
        
        # Load metadata
        logger.info(f"Loading metadata from {metadata_path}")
        segments = segmenter.load_metadata()
        logger.info(f"Found {len(segments)} segments to process")
        
        # Export video segments
        logger.info(f"Processing video segments from {input_video}")
        success = segmenter.export_video_segments(
            input_video=input_video,
            output_dir=output_dir / 'video_chunks',
            error_log=error_log
        )
        
        # Create video index
        logger.info("Creating video index")
        segmenter.create_video_index(output_dir / 'video_index.json')
        
        return success
        
    except Exception as e:
        logger.error(f"Error processing interview: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Process interview videos into transcript chunks and video segments")
    parser.add_argument("input_video", type=str, help="Path to input video file (.mp4)")
    parser.add_argument("metadata", type=str, help="Path to chunk metadata file (chunk_metadata.json)")
    parser.add_argument("--output-dir", type=str, default=".", help="Output directory for all generated files")
    parser.add_argument("--error-log", type=str, default="errors.log", help="Path to error log file")
    
    args = parser.parse_args()
    
    # Convert paths
    input_video = Path(args.input_video)
    metadata_path = Path(args.metadata)
    output_dir = Path(args.output_dir)
    error_log = Path(args.error_log)
    
    # Validate inputs
    if not input_video.exists():
        logger.error(f"Input video not found: {input_video}")
        sys.exit(1)
    if not metadata_path.exists():
        logger.error(f"Metadata file not found: {metadata_path}")
        sys.exit(1)
        
    # Create directories
    setup_directories(output_dir)
    
    # Process interview
    success = process_interview(
        input_video=input_video,
        metadata_path=metadata_path,
        output_dir=output_dir,
        error_log=error_log
    )
    
    # Exit with appropriate status
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
