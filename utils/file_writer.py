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
    def __init__(self, output_dir: str, job_id: Optional[str] = None):
        """Initialize FileWriter with output directory and optional job ID.
        
        Args:
            output_dir: Base output directory
            job_id: Optional job ID for organizing outputs. If not provided,
                   will generate one using current timestamp
        """
        self.output_dir = Path(output_dir)
        self.job_id = job_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create job-specific output directory
        self.job_dir = self.output_dir / self.job_id
        self.job_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.video_dir = self.job_dir / "video_chunks"
        self.video_dir.mkdir(exist_ok=True)
        
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
                f.write("# Interview Transcript\n\n")
                
                for i, chunk in enumerate(chunks, 1):
                    chunk_data = self._get_chunk_data(chunk)
                    
                    # Get timing info, supporting both field name formats
                    start_time = chunk_data.get("start_time") or chunk_data.get("start", 0)
                    end_time = chunk_data.get("end_time") or chunk_data.get("end", 0)
                    
                    # Write chunk header with timestamps
                    f.write(f"## Chunk {i} [{self.format_timestamp(start_time)} - {self.format_timestamp(end_time)}]\n\n")
                    
                    # Write question if present
                    if "question" in chunk_data:
                        f.write(f"**Q:** {chunk_data['question']}\n\n")
                    
                    # Write response text
                    text = chunk_data.get("response_text") or chunk_data.get("text", "")
                    f.write(f"{text}\n\n")
                    
                    # Add separator between chunks
                    f.write("---\n\n")
                    
            logger.info(f"Wrote transcript chunks to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to write transcript chunks: {str(e)}")
            raise
            
    def write_chunk_metadata(self, chunks: List[Union[Dict, TranscriptSegment]]) -> None:
        """Write chunk metadata to JSON file."""
        try:
            output_path = self.job_dir / "chunk_metadata.json"
            
            metadata = []
            for chunk in chunks:
                chunk_data = self._get_chunk_data(chunk)
                
                # Get timing info, supporting both field name formats
                start_time = chunk_data.get("start_time") or chunk_data.get("start", 0)
                end_time = chunk_data.get("end_time") or chunk_data.get("end", 0)
                
                metadata.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": chunk_data["text"],
                    "speaker": chunk_data.get("speaker", "unknown"),
                    "question": chunk_data.get("question", ""),
                    "question_id": chunk_data.get("question_id", ""),
                    "similarity_score": chunk_data.get("similarity_score", 0.0),
                    "video_path": str(self.video_dir / f"chunk_{len(metadata)+1}.mp4")
                })
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"chunks": metadata}, f, indent=2)
                
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
