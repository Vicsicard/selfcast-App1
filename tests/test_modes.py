"""
Integration tests for Transcript Builder modes
Tests both Whisper and VTT modes for correct functionality
"""
import os
import json
import shutil
from pathlib import Path
import pytest
from loguru import logger

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from transcript_builder import process_whisper_mode, process_vtt_mode
from utils.vtt_parser import VTTParser
from utils.video_cutter import VideoCutter
from utils.file_writer import FileWriter

# Test data
TEST_DATA = Path(__file__).parent / "data"
TEST_OUTPUT = Path(__file__).parent / "test_output"
TEST_VTT = TEST_DATA / "test.vtt"
TEST_MP4 = TEST_DATA / "test.mp4"

def setup_module():
    """Setup test environment."""
    # Create test directories
    TEST_DATA.mkdir(exist_ok=True)
    TEST_OUTPUT.mkdir(exist_ok=True)
    
    # Create test VTT file if it doesn't exist
    if not TEST_VTT.exists():
        with open(TEST_VTT, "w", encoding="utf-8") as f:
            f.write("""WEBVTT

00:00:00.000 --> 00:00:05.500
[Interviewer] Tell me about your background.

00:00:06.000 --> 00:00:15.000
[John] I've been working in tech for 10 years.

00:00:15.500 --> 00:00:25.000
[John] Started my first company right out of college.""")

def teardown_module():
    """Cleanup test environment."""
    if TEST_OUTPUT.exists():
        shutil.rmtree(TEST_OUTPUT)

@pytest.fixture
def file_writer():
    """Create FileWriter instance for testing."""
    return FileWriter(str(TEST_OUTPUT), job_id="test_job")

def test_whisper_mode_without_vtt():
    """Test that Whisper mode works correctly without VTT file."""
    try:
        # Process in Whisper mode
        transcript = process_whisper_mode(TEST_MP4, TEST_OUTPUT)
        
        # Verify transcript structure
        assert isinstance(transcript, list)
        for segment in transcript:
            assert "start" in segment
            assert "end" in segment
            assert "text" in segment
            
    except Exception as e:
        logger.error(f"Whisper mode test failed: {str(e)}")
        raise

def test_vtt_mode_activation():
    """Test that VTT mode activates correctly with both flags."""
    try:
        # Process in VTT mode
        transcript = process_vtt_mode(TEST_VTT)
        
        # Verify transcript structure
        assert isinstance(transcript, list)
        for segment in transcript:
            assert "start" in segment
            assert "end" in segment
            assert "text" in segment
            assert "speaker" in segment
            
    except Exception as e:
        logger.error(f"VTT mode test failed: {str(e)}")
        raise

def test_md_chunks_match_vtt(file_writer):
    """Test that markdown chunks match VTT transcript content."""
    try:
        # Parse VTT file
        vtt_parser = VTTParser(TEST_VTT)
        transcript = vtt_parser.parse()
        
        # Write chunks
        file_writer.write_transcript_chunks(transcript)
        
        # Read generated markdown
        md_path = file_writer.job_dir / "transcript_chunks.md"
        assert md_path.exists()
        
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        
        # Verify each VTT segment appears in markdown
        for segment in transcript:
            assert segment.text in md_content
            if segment.speaker:
                assert segment.speaker in md_content
                
    except Exception as e:
        logger.error(f"Markdown chunk test failed: {str(e)}")
        raise

def test_video_chunks_match_vtt():
    """Test that video chunks match VTT timestamps."""
    try:
        # Parse VTT file
        vtt_parser = VTTParser(TEST_VTT)
        transcript = vtt_parser.parse()
        
        # Initialize video cutter
        video_cutter = VideoCutter(str(TEST_MP4), str(TEST_OUTPUT))
        
        # Process chunks
        chunks = video_cutter.process_chunks([chunk.to_dict() for chunk in transcript])
        
        # Verify video index
        video_index = video_cutter.create_video_index()
        assert len(video_index["chunks"]) == len(transcript)
        
        # Verify each chunk's timestamps
        chunks_dir = Path(TEST_OUTPUT) / "video_chunks"
        assert chunks_dir.exists()
        
        for chunk, vtt_segment in zip(chunks, transcript):
            # Verify chunk file exists
            chunk_path = chunks_dir / chunk["video_path"]
            assert chunk_path.exists()
            
            # Verify timestamps match
            assert abs(chunk["start"] - vtt_segment.start_time) < 0.1
            assert abs(chunk["end"] - vtt_segment.end_time) < 0.1
            
    except Exception as e:
        logger.error(f"Video chunk test failed: {str(e)}")
        raise

def test_output_structure(file_writer):
    """Test that output structure is consistent between modes."""
    try:
        # Process some test data
        transcript = process_vtt_mode(TEST_VTT)
        file_writer.write_transcript_chunks(transcript)
        file_writer.write_chunk_metadata(transcript)
        
        # Verify directory structure
        job_dir = file_writer.job_dir
        assert job_dir.exists()
        assert (job_dir / "video_chunks").exists()
        assert (job_dir / "transcript_chunks.md").exists()
        assert (job_dir / "chunk_metadata.json").exists()
        
        # Verify metadata format
        with open(job_dir / "chunk_metadata.json", "r") as f:
            metadata = json.load(f)
            assert "job_id" in metadata
            assert "generated_at" in metadata
            assert "total_chunks" in metadata
            assert "chunks" in metadata
            
    except Exception as e:
        logger.error(f"Output structure test failed: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main([__file__])
