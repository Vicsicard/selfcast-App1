"""
Test video segmentation functionality.
"""
import json
import os
from pathlib import Path
import pytest
import ffmpeg
from unittest.mock import patch, MagicMock
from utils.video_segmenter import VideoSegmenter, VideoSegment

# Test data directory
TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR.parent / 'data'
TEMP_DIR = TEST_DIR / 'temp'

@pytest.fixture
def sample_metadata():
    """Create sample chunk metadata for testing."""
    metadata = [
        {
            "chunk_id": "intro_001",
            "question_id": "01",
            "start_time": "00:00:00",
            "end_time": "00:00:15"
        },
        {
            "chunk_id": "pivot_002",
            "question_id": "02",
            "start_time": "00:00:16",
            "end_time": "00:00:45"
        },
        {
            "chunk_id": "challenge_003",
            "question_id": "03",
            "start_time": "00:00:46",
            "end_time": "00:01:00"
        }
    ]
    
    # Create temp directory if it doesn't exist
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write metadata to file
    metadata_path = TEMP_DIR / 'chunk_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
        
    return metadata_path

@patch('ffmpeg.run')
def test_video_segmentation(mock_ffmpeg_run, sample_metadata):
    """Test the complete video segmentation process."""
    # Initialize segmenter
    segmenter = VideoSegmenter(sample_metadata)
    
    # Load metadata
    segments = segmenter.load_metadata()
    assert len(segments) == 3
    
    # Verify segment data
    assert segments[0].chunk_id == "intro_001"
    assert segments[0].start_time == "00:00:00"
    assert segments[0].end_time == "00:00:15"
    
    # Create video chunks directory
    video_chunks_dir = TEMP_DIR / 'video_chunks'
    video_chunks_dir.mkdir(exist_ok=True)
    
    # Create a dummy input video for testing
    input_video = TEMP_DIR / 'input.mp4'
    input_video.touch()
    
    # Mock successful ffmpeg runs
    mock_ffmpeg_run.return_value = None
    
    # Export video segments
    success = segmenter.export_video_segments(
        input_video=input_video,
        output_dir=video_chunks_dir,
        error_log=TEMP_DIR / 'errors.log'
    )
    assert success is True
    
    # Verify ffmpeg was called correct number of times
    assert mock_ffmpeg_run.call_count == 3
    
    # Create video index
    segmenter.create_video_index(TEMP_DIR / 'video_index.json')
    
    # Verify outputs exist
    assert (TEMP_DIR / 'video_index.json').exists()
    assert (TEMP_DIR / 'errors.log').exists()
    
    # Verify video index structure
    with open(TEMP_DIR / 'video_index.json') as f:
        index = json.load(f)
        assert len(index) == 3  # Should match number of segments
        
        # Check first entry
        assert index[0]["chunk_id"] == "intro_001"
        assert index[0]["filename"] == "Q01_intro_001.mp4"
        assert index[0]["start_time"] == "00:00:00"
        assert index[0]["end_time"] == "00:00:15"
        assert index[0]["question_id"] == "01"

@patch('ffmpeg.run')
def test_error_handling(mock_ffmpeg_run, sample_metadata):
    """Test error handling and logging."""
    segmenter = VideoSegmenter(sample_metadata)
    segments = segmenter.load_metadata()
    
    # Create directories
    video_chunks_dir = TEMP_DIR / 'video_chunks'
    video_chunks_dir.mkdir(exist_ok=True)
    input_video = TEMP_DIR / 'input.mp4'
    input_video.touch()
    error_log = TEMP_DIR / 'errors_test.log'
    
    # Mock ffmpeg failure for second segment
    def mock_run(*args, **kwargs):
        if "Q02_pivot_002.mp4" in str(args):
            error = ffmpeg.Error("Mock error", "", "Failed to process video")
            error.stderr = b"Failed to process video"
            raise error
        return None
        
    mock_ffmpeg_run.side_effect = mock_run
    
    # Export video segments
    success = segmenter.export_video_segments(
        input_video=input_video,
        output_dir=video_chunks_dir,
        error_log=error_log
    )
    
    # Should return False due to one failure
    assert success is False
    
    # Verify error was logged
    assert error_log.exists()
    with open(error_log) as f:
        log_content = f.read()
        assert "pivot_002" in log_content
        assert "Failed to process video" in log_content
    
    # Create video index
    index_path = TEMP_DIR / 'video_index_test.json'
    segmenter.create_video_index(index_path)
    
    # Verify failed segment is excluded from index
    with open(index_path) as f:
        index = json.load(f)
        assert len(index) == 2  # Only successful segments
        chunk_ids = [entry["chunk_id"] for entry in index]
        assert "pivot_002" not in chunk_ids

def test_timestamp_conversion():
    """Test timestamp conversion utilities."""
    segmenter = VideoSegmenter(TEMP_DIR / 'dummy.json')
    
    # Test seconds to HH:MM:SS
    assert segmenter._format_timestamp(3661.5) == "01:01:01"
    assert segmenter._format_timestamp(0) == "00:00:00"
    assert segmenter._format_timestamp(7323) == "02:02:03"
    
    # Test HH:MM:SS to seconds
    assert segmenter._timestamp_to_seconds("01:01:01") == 3661
    assert segmenter._timestamp_to_seconds("00:00:00") == 0
    assert segmenter._timestamp_to_seconds("02:02:03") == 7323

if __name__ == '__main__':
    pytest.main([__file__])
