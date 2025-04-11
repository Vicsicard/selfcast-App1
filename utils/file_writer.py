"""
File Writer Module

Handles writing transcript chunks and metadata to files in consistent formats:
- transcript_chunks.md: Human-readable markdown with proper formatting
- chunk_metadata.json: Structured data about each chunk
- chunk_vectors.json: Vector embeddings for each chunk
- errors.log: Any errors encountered during processing
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
from loguru import logger

from .models import TranscriptSegment

class FileWriter:
    """Handles writing all output files in the required structure."""
    
    def __init__(self, output_dir: str, category: Optional[str] = None, job_id: Optional[str] = None):
        """Initialize FileWriter with output directory and optional job ID.
        
        Args:
            output_dir: Base output directory
            category: Category of the transcript (e.g., narrative_defense)
            job_id: Optional job ID for organizing outputs. If not provided,
                   will generate one using current timestamp and category
        """
        self.output_dir = Path(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.job_id = job_id or f"{timestamp}_{category}" if category else timestamp
        
        # Create job-specific output directory
        self.job_dir = self.output_dir / self.job_id
        self.job_dir.mkdir(parents=True, exist_ok=True)
        
        # Create video chunks directory
        self.video_dir = self.job_dir / "video_chunks"
        self.video_dir.mkdir(exist_ok=True)
        
        # Initialize empty error log
        error_log = self.job_dir / "errors.log"
        if not error_log.exists():
            error_log.touch()
            
        logger.info(f"Initialized output directory structure at {self.job_dir}")
        
    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        
    def _get_chunk_data(self, chunk: Union[Dict, TranscriptSegment]) -> Dict:
        """Extract data from chunk regardless of type."""
        if isinstance(chunk, TranscriptSegment):
            return {
                "start": chunk.start,
                "end": chunk.end,
                "text": chunk.text,
                "speaker": chunk.speaker
            }
        return chunk
        
    def write_transcript_chunks(self, chunks: List[Union[Dict, TranscriptSegment]]) -> None:
        """Write transcript chunks to markdown file with proper formatting."""
        try:
            output_path = self.job_dir / "transcript_chunks.md"
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("# Speaker 2 Transcript Chunks\n\n")
                
                for i, chunk in enumerate(chunks, 1):
                    chunk_data = self._get_chunk_data(chunk)
                    
                    # Get timing info
                    start_time = chunk_data.get("start_time") or chunk_data.get("start", 0)
                    end_time = chunk_data.get("end_time") or chunk_data.get("end", 0)
                    
                    # Write chunk in required format
                    f.write(f"## [Chunk {i:02d}]\n")
                    f.write(f"**Timestamp**: {self.format_timestamp(start_time)} — {self.format_timestamp(end_time)}\n")
                    f.write(f"> Speaker 2: {chunk_data.get('text', '').strip()}\n\n")
                    
            logger.info(f"Wrote transcript chunks to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to write transcript chunks: {str(e)}")
            raise
            
    def write_chunk_metadata(self, chunks: List[Union[Dict, TranscriptSegment]]) -> None:
        """Write chunk metadata to JSON file."""
        try:
            output_path = self.job_dir / "chunk_metadata.json"
            
            metadata = []
            for i, chunk in enumerate(chunks, 1):
                chunk_data = self._get_chunk_data(chunk)
                
                # Get timing info
                start_time = chunk_data.get("start_time") or chunk_data.get("start", 0)
                end_time = chunk_data.get("end_time") or chunk_data.get("end", 0)
                duration = end_time - start_time
                
                metadata.append({
                    "chunk_id": f"chunk_{i:02d}",
                    "start_time": self.format_timestamp(start_time),
                    "end_time": self.format_timestamp(end_time),
                    "duration": round(duration, 3),
                    "text": chunk_data["text"].strip(),
                    "video_path": str(self.video_dir / f"chunk_{i:02d}.mp4"),
                    "audio_path": str(self.video_dir / f"chunk_{i:02d}.m4a"),
                    "subtitle_path": str(self.video_dir / f"chunk_{i:02d}.vtt")
                })
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({
                    "job_id": self.job_id,
                    "total_chunks": len(chunks),
                    "chunks": metadata
                }, f, indent=2)
                
            logger.info(f"Wrote chunk metadata to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to write chunk metadata: {str(e)}")
            raise
            
    def write_chunk_vectors(self, chunk_vectors: List[List[float]]) -> None:
        """Write chunk vectors to JSON file."""
        output_path = self.job_dir / "chunk_vectors.json"
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chunk_vectors, f)
                
        except Exception as e:
            logger.error(f"Failed to write chunk vectors: {str(e)}")
            raise
            
    def write_video_index(self, chunks: List[Union[Dict, TranscriptSegment]]) -> None:
        """Write video index mapping to JSON file.
        
        Format:
        {
            "chunks": [
                {
                    "chunk_id": "chunk_001",
                    "video_file": "chunk_001.mp4",
                    "start": "00:14:32",
                    "end": "00:17:01"
                },
                ...
            ]
        }
        """
        try:
            output_path = self.job_dir / "video_index.json"
            
            # Build index entries
            index_entries = []
            for i, chunk in enumerate(chunks, 1):
                chunk_data = self._get_chunk_data(chunk)
                
                # Get timing info
                start_time = chunk_data.get("start_time") or chunk_data.get("start", 0)
                end_time = chunk_data.get("end_time") or chunk_data.get("end", 0)
                
                # Create index entry
                entry = {
                    "chunk_id": f"chunk_{i:03d}",
                    "video_file": f"chunk_{i:03d}.mp4",
                    "start": self.format_timestamp(start_time),
                    "end": self.format_timestamp(end_time)
                }
                index_entries.append(entry)
            
            # Write index file
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"chunks": index_entries}, f, indent=2)
                
            logger.info(f"Wrote video index to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to write video index: {str(e)}")
            raise
            
    def write_error_log(self, error: str) -> None:
        """Write error message to log file."""
        log_path = self.job_dir / "errors.log"
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {error}\n")
                
        except Exception as e:
            logger.error(f"Failed to write to error log: {str(e)}")
            # Don't raise here to avoid error cascade
            
    def write_all_outputs(self, chunks: List[Union[Dict, TranscriptSegment]]) -> None:
        """Write all required output files in a single call.
        
        This ensures all files are written consistently:
        - transcript_chunks.md
        - chunk_metadata.json
        - video_index.json
        - errors.log (if any errors occurred)
        
        Args:
            chunks: List of transcript chunks to process
        """
        try:
            # Write transcript chunks
            self.write_transcript_chunks(chunks)
            logger.info("✓ Wrote transcript_chunks.md")
            
            # Write chunk metadata
            self.write_chunk_metadata(chunks)
            logger.info("✓ Wrote chunk_metadata.json")
            
            # Write video index
            self.write_video_index(chunks)
            logger.info("✓ Wrote video_index.json")
            
            # Verify output structure
            required_files = [
                "transcript_chunks.md",
                "chunk_metadata.json",
                "video_index.json",
                "errors.log"
            ]
            
            missing_files = []
            for file in required_files:
                if not (self.job_dir / file).exists():
                    missing_files.append(file)
                    
            if missing_files:
                raise FileNotFoundError(f"Missing required output files: {', '.join(missing_files)}")
                
            # Verify video chunks directory
            if not self.video_dir.exists():
                raise FileNotFoundError("Missing video_chunks directory")
                
            logger.info(f"Successfully wrote all outputs to {self.job_dir}")
            
        except Exception as e:
            error_msg = f"Failed to write outputs: {str(e)}"
            logger.error(error_msg)
            self.write_error_log(error_msg)
            raise
