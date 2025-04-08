"""
Video cutting utilities for extracting segments from MP4 files.
"""
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Union
from loguru import logger

from .models import TranscriptSegment

class VideoCutter:
    def __init__(self, input_path: str, output_dir: str):
        """Initialize video cutter with input file and output directory."""
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input video not found: {input_path}")
            
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def cut_segment(self, start_time: float, end_time: float, output_path: str) -> bool:
        """Cut video segment using ffmpeg."""
        try:
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build ffmpeg command
            duration = end_time - start_time
            command = [
                "ffmpeg",
                "-i", str(self.input_path),
                "-ss", str(start_time),
                "-t", str(duration),
                "-c:v", "copy",  # Copy video codec
                "-c:a", "copy",  # Copy audio codec
                "-y",  # Overwrite output
                str(output_path)
            ]
            
            # Run ffmpeg
            logger.info(f"Cutting segment [{start_time:.2f} - {end_time:.2f}] to {output_path}")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"ffmpeg failed: {result.stderr}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to cut segment: {str(e)}")
            return False
    
    def _get_chunk_timing(self, chunk: Union[Dict, TranscriptSegment]) -> tuple[float, float]:
        """Extract start and end times from chunk, handling different types."""
        if isinstance(chunk, TranscriptSegment):
            return chunk.start, chunk.end
        else:
            # Try different field names for compatibility
            start_time = chunk.get("start_time") or chunk.get("start", 0.0)
            end_time = chunk.get("end_time") or chunk.get("end", 0.0)
            return start_time, end_time
    
    def process_chunks(self, chunks: List[Union[Dict, TranscriptSegment]]) -> List[Dict]:
        """Process a list of transcript chunks, cutting video segments for each."""
        processed_chunks = []
        
        for i, chunk in enumerate(chunks, 1):
            # Get timing info
            start_time, end_time = self._get_chunk_timing(chunk)
            
            # Generate output path
            output_path = self.output_dir / f"chunk_{i:03d}.mp4"
            
            # Cut video segment
            success = self.cut_segment(start_time, end_time, str(output_path))
            
            if success:
                # Convert chunk to dict if it's a TranscriptSegment
                if isinstance(chunk, TranscriptSegment):
                    chunk_data = {
                        "start_time": chunk.start,
                        "end_time": chunk.end,
                        "text": chunk.text,
                        "speaker": chunk.speaker,
                        "video_path": str(output_path)
                    }
                else:
                    # Make a copy of the dict
                    chunk_data = dict(chunk)
                    chunk_data.update({
                        "start_time": start_time,
                        "end_time": end_time,
                        "video_path": str(output_path)
                    })
                
                processed_chunks.append(chunk_data)
            else:
                logger.error(f"Failed to process chunk {i}")
        
        return processed_chunks
