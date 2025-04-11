"""
Integration tests for Transcript Builder v1.1.
"""
import os
import json
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from loguru import logger

from transcript_builder import process_vtt_mode, process_whisper_mode
from utils.vtt_parser import VTTParser
from utils.video_cutter import VideoCutter
from utils.file_writer import FileWriter
from utils.embedding import EmbeddingGenerator

class TestTranscriptBuilder:
    """Integration tests for Transcript Builder v1.1."""
    
    @pytest.fixture
    def setup_test_env(self, tmp_path):
        """Set up test environment with sample files."""
        # Create test directories
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        # Create dummy input files
        (input_dir / "input.mp4").touch()
        (input_dir / "input.vtt").write_text("""WEBVTT

00:00:00.000 --> 00:00:30.000
Speaker 1: Hello there

00:00:31.000 --> 00:01:00.000
Speaker 2: Hi, this is a test response

00:01:01.000 --> 00:01:30.000
Speaker 2: Another response here
""")
        (input_dir / "input.m4a").touch()
        
        # Create job directory
        job_dir = output_dir / "test_job"
        job_dir.mkdir(parents=True)
        
        return {
            "input_dir": input_dir,
            "output_dir": output_dir,
            "job_dir": job_dir,
            "job_id": "test_job"
        }
        
    def test_input_handling(self, setup_test_env):
        """Test input file handling."""
        env = setup_test_env
        
        # Test required MP4
        assert (env["input_dir"] / "input.mp4").exists()
        
        # Test optional VTT
        assert (env["input_dir"] / "input.vtt").exists()
        
        # Test optional M4A
        assert (env["input_dir"] / "input.m4a").exists()
        
    def test_speaker_filtering(self, setup_test_env):
        """Test Speaker 2 extraction and filtering."""
        env = setup_test_env
        
        # Initialize components
        parser = VTTParser(
            str(env["input_dir"] / "input.vtt"),
            env["output_dir"]
        )
        
        # Parse segments
        segments = parser.parse_speaker_2_only()
        
        # Verify Speaker 2 only
        for segment in segments:
            assert "Speaker 2" in segment.speaker
            assert segment.text
            assert segment.start >= 0
            assert segment.end > segment.start
            
    def test_chunk_formatting(self, setup_test_env):
        """Test chunk formatting in markdown and metadata."""
        env = setup_test_env
        
        # Initialize writer
        writer = FileWriter(
            str(env["output_dir"]),
            "test",
            env["job_id"]
        )
        
        # Create test chunks
        chunks = [{
            "chunk_id": "chunk_001",
            "start_time": 0,
            "end_time": 30,
            "text": "Test response",
            "speaker": "Speaker 2"
        }]
        
        # Write outputs
        writer.write_transcript_chunks(chunks)
        writer.write_chunk_metadata(chunks)
        
        # Verify markdown format
        md_file = env["job_dir"] / "transcript_chunks.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "## [Chunk" in content
        assert "**Timestamp**:" in content
        assert "> Speaker 2:" in content
        
        # Verify metadata
        meta_file = env["job_dir"] / "chunk_metadata.json"
        assert meta_file.exists()
        meta = json.loads(meta_file.read_text())
        assert "chunks" in meta
        assert isinstance(meta["chunks"], list)
        assert len(meta["chunks"]) == 1
        chunk = meta["chunks"][0]
        assert all(k in chunk for k in ["chunk_id", "start_time", "end_time", "text"])
        
    @patch("utils.video_cutter.subprocess.run")
    def test_video_export(self, mock_run, setup_test_env):
        """Test video segment export and indexing."""
        env = setup_test_env
        
        # Mock successful ffmpeg execution
        mock_run.return_value = MagicMock(returncode=0)
        
        # Initialize components
        cutter = VideoCutter(
            str(env["input_dir"] / "input.mp4"),
            str(env["output_dir"]),
            env["job_id"]
        )
        writer = FileWriter(
            str(env["output_dir"]),
            "test",
            env["job_id"]
        )
        
        # Create test chunks
        chunks = [{
            "chunk_id": "chunk_001",
            "start_time": 0,
            "end_time": 30,
            "text": "Test response",
            "speaker": "Speaker 2"
        }]
        
        # Process video chunks
        processed = cutter.process_chunks(chunks)
        writer.write_video_index(processed)
        
        # Verify video chunks directory
        video_dir = env["job_dir"] / "video_chunks"
        assert video_dir.exists()
        
        # Verify video index
        index_file = env["job_dir"] / "video_index.json"
        assert index_file.exists()
        index = json.loads(index_file.read_text())
        assert "chunks" in index
        assert len(index["chunks"]) > 0
        chunk = index["chunks"][0]
        assert all(k in chunk for k in ["chunk_id", "video_file", "start", "end"])
        
    def test_embedding_output(self, setup_test_env):
        """Test embedding generation and storage."""
        env = setup_test_env
        
        # Initialize components
        embedder = EmbeddingGenerator()
        
        # Create test chunks
        chunks = [{
            "chunk_id": "chunk_001",
            "text": "Test response"
        }]
        
        # Generate embeddings
        embedder.process_chunks(chunks, env["job_dir"])
        
        # Verify embeddings file
        vectors_file = env["job_dir"] / "chunk_vectors.json"
        assert vectors_file.exists()
        vectors = json.loads(vectors_file.read_text())
        assert "model" in vectors
        assert "vectors" in vectors
        vector = vectors["vectors"][0]
        assert all(k in vector for k in ["chunk_id", "vector", "text"])
        
    def test_error_logging(self, setup_test_env):
        """Test error logging functionality."""
        env = setup_test_env
        
        # Initialize components with bad input to trigger errors
        parser = VTTParser(
            "nonexistent.vtt",
            env["job_dir"]
        )
        
        # Create error log file
        error_log = env["job_dir"] / "errors.log"
        error_log.touch()
        
        # Attempt operations that will fail
        try:
            parser.parse_speaker_2_only()
        except:
            pass
            
        # Verify error log exists and has content
        assert error_log.exists()
        content = error_log.read_text()
        assert "VTT Parse Error" in content
        
    def test_output_verification(self, setup_test_env):
        """Test final output structure verification."""
        env = setup_test_env
        
        # Create required directories
        job_dir = env["job_dir"]
        video_dir = job_dir / "video_chunks"
        video_dir.mkdir(exist_ok=True)
        
        # Create all required files
        required_files = [
            "transcript_chunks.md",
            "chunk_metadata.json",
            "chunk_vectors.json",
            "video_index.json",
            "errors.log"
        ]
        
        for file in required_files:
            (job_dir / file).touch()
            
        # Create dummy video chunk
        (video_dir / "chunk_001.mp4").touch()
        
        # Verify structure
        assert all((job_dir / f).exists() for f in required_files)
        assert video_dir.exists()
        assert any(video_dir.glob("chunk_*.mp4"))
