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
from typing import Dict, List
from loguru import logger
from .chunk_builder import TranscriptChunk

class FileWriter:
    def __init__(self, output_dir: str):
        """Initialize FileWriter with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
    def write_transcript_chunks(self, chunks: List[TranscriptChunk]) -> None:
        """
        Write transcript chunks to markdown file following strict formatting rules:
        - Second-level header with question ID and label
        - Matched question text
        - Timestamp range
        - Client responses in blockquote format
        - One empty line between chunks
        """
        output_path = self.output_dir / "transcript_chunks.md"
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for i, chunk in enumerate(chunks):
                    # Write header with question ID and label
                    question_id = chunk.question_id
                    question_label = question_id  # TODO: Get actual label from questions
                    f.write(f"## [{question_id}] {question_label}\n\n")
                    
                    # Write matched question
                    f.write(f"**Matched Question**: {chunk.question_text}\n\n")
                    
                    # Write timestamp range
                    start_time = self.format_timestamp(chunk.start_time)
                    end_time = self.format_timestamp(chunk.end_time)
                    f.write(f"**Timestamp**: {start_time} — {end_time}\n\n")
                    
                    # Write client responses in blockquote format
                    responses = chunk.response_text.strip().split("\n")
                    for response in responses:
                        if response.strip():
                            f.write(f"> Speaker 1: {response.strip()}\n")
                    
                    # Add empty line between chunks (except after last chunk)
                    if i < len(chunks) - 1:
                        f.write("\n\n")
        except Exception as e:
            logger.error(f"Error writing transcript chunks: {str(e)}")
            self.write_error(f"Failed to write transcript chunks: {str(e)}")
                
    def write_chunk_metadata(self, chunks: List[TranscriptChunk]) -> None:
        """Write chunk metadata to JSON file."""
        output_path = self.output_dir / "chunk_metadata.json"
        
        try:
            metadata = [{
                "chunk_id": chunk.chunk_id,
                "question_id": chunk.question_id,
                "start_time": chunk.start_time,
                "end_time": chunk.end_time,
                "similarity_score": chunk.similarity_score
            } for chunk in chunks]
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing chunk metadata: {str(e)}")
            self.write_error(f"Failed to write chunk metadata: {str(e)}")
            
    def write_chunk_vectors(self, chunk_vectors: Dict[str, List[float]]) -> None:
        """Write chunk vectors to JSON file."""
        output_path = self.output_dir / "chunk_vectors.json"
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chunk_vectors, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing chunk vectors: {str(e)}")
            self.write_error(f"Failed to write chunk vectors: {str(e)}")
    
    def write_error(self, error_msg: str) -> None:
        """Write error message to log file."""
        output_path = self.output_dir / "errors.log"
        try:
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(f"{error_msg}\n")
        except Exception as e:
            logger.error(f"Error writing to error log: {str(e)}")
