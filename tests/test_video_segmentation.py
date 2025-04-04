"""
Integration test for video segmentation functionality.
"""
import os
import json
from pathlib import Path
import pytest
from unittest.mock import patch
from utils.video_segmenter import VideoSegmenter

# Test directories
TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / 'test_data'
VIDEO_CHUNKS_DIR = TEST_DIR / 'video_chunks'
VIDEO_INDEX = TEST_DIR / 'video_index.json'
ERROR_LOG = TEST_DIR / 'errors.log'

@patch('ffmpeg.run')
def test_video_segmentation_integration(mock_ffmpeg_run):
    """Test complete video segmentation workflow."""
    # Clean up any existing test files
    if VIDEO_CHUNKS_DIR.exists():
        for file in VIDEO_CHUNKS_DIR.glob('*.mp4'):
            file.unlink()
        VIDEO_CHUNKS_DIR.rmdir()
    if VIDEO_INDEX.exists():
        VIDEO_INDEX.unlink()
    if ERROR_LOG.exists():
        ERROR_LOG.unlink()
        
    # Create test video file
    input_video = DATA_DIR / 'test_video.mp4'
    if not input_video.exists():
        input_video.touch()  # Create empty file for testing
        
    # Initialize segmenter
    metadata_path = DATA_DIR / 'chunk_metadata.json'
    segmenter = VideoSegmenter(metadata_path)
    
    # Load metadata
    segments = segmenter.load_metadata()
    assert len(segments) == 3
    
    # Mock successful ffmpeg runs
    mock_ffmpeg_run.return_value = None
    
    # Export segments
    success = segmenter.export_video_segments(
        input_video=input_video,
        output_dir=VIDEO_CHUNKS_DIR,
        error_log=ERROR_LOG
    )
    
    # Verify success
    assert success is True
    
    # Create index
    segmenter.create_video_index(VIDEO_INDEX)
    
    # Verify directory structure
    assert VIDEO_CHUNKS_DIR.exists()
    assert VIDEO_INDEX.exists()
    assert ERROR_LOG.exists()
    
    # Verify video index structure
    with open(VIDEO_INDEX) as f:
        index = json.load(f)
        assert len(index) == 3
        
        # Check first entry
        entry = index[0]
        assert "chunk_id" in entry
        assert "filename" in entry
        assert "start_time" in entry
        assert "end_time" in entry
        assert "question_id" in entry
        
        # Verify filename format
        assert entry["filename"].startswith("Q")
        assert entry["filename"].endswith(".mp4")
        
    # Clean up
    if VIDEO_CHUNKS_DIR.exists():
        for file in VIDEO_CHUNKS_DIR.glob('*.mp4'):
            file.unlink()
        VIDEO_CHUNKS_DIR.rmdir()
    if VIDEO_INDEX.exists():
        VIDEO_INDEX.unlink()
    if ERROR_LOG.exists():
        ERROR_LOG.unlink()

if __name__ == '__main__':
    pytest.main([__file__])
