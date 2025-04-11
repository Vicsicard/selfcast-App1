"""
Video cutting utilities with robust error handling.
"""
from pathlib import Path
from typing import List, Dict, Optional, Union
import subprocess
from loguru import logger

from .error_handler import ErrorHandler, ErrorType
from .models import TranscriptSegment

class VideoCutter:
    """Handles cutting video files into segments with error handling."""
    
    def __init__(self, input_path: str, output_dir: str, job_id: str):
        """Initialize video cutter with error handling.
        
        Args:
            input_path: Path to input video file
            output_dir: Base output directory
            job_id: Job ID for organizing outputs
        """
        self.input_path = Path(input_path)
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input video not found: {input_path}")
            
        self.output_dir = Path(output_dir) / job_id / "video_chunks"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize error handler
        self.error_handler = ErrorHandler(Path(output_dir) / job_id)
        
    def _format_timecode(self, seconds: float) -> str:
        """Convert seconds to ffmpeg timecode format (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        
    def cut_segment(self, chunk_num: int, start_time: float, end_time: float) -> Optional[str]:
        """Cut a single video segment using ffmpeg.
        
        Args:
            chunk_num: Chunk number (for output filename)
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Path to output video file or None if failed
        """
        chunk_id = f"chunk_{chunk_num:03d}"
        output_path = self.output_dir / f"{chunk_id}.mp4"
        
        # Skip if file already exists
        if output_path.exists():
            logger.info(f"Skipping existing chunk: {output_path}")
            return str(output_path)
            
        try:
            # Format timecodes for ffmpeg
            start_tc = self._format_timecode(start_time)
            duration = end_time - start_time
            
            # Construct ffmpeg command
            cmd = [
                "ffmpeg",
                "-i", str(self.input_path),
                "-ss", start_tc,
                "-t", str(duration),
                "-c:v", "libx264",    # Use H.264 codec
                "-preset", "fast",     # Fast encoding
                "-c:a", "aac",        # AAC audio codec
                "-y",                  # Overwrite output
                str(output_path)
            ]
            
            # Run ffmpeg
            logger.info(f"Cutting {chunk_id}: {start_tc} to {self._format_timecode(end_time)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg failed: {result.stderr}")
                
            return str(output_path)
            
        except Exception as e:
            self.error_handler.log_video_error(
                f"Failed to cut segment: {str(e)}",
                chunk_id
            )
            return None
            
    def process_chunks(self, segments: List[Union[Dict, TranscriptSegment]]) -> List[Dict]:
        """Process all chunks from the provided segments.
        
        Args:
            segments: List of segment dictionaries or TranscriptSegment objects
            
        Returns:
            List of processed chunks with video paths added
        """
        processed_chunks = []
        failed_chunks = []
        
        for i, segment in enumerate(segments, 1):
            try:
                chunk = segment.to_dict() if isinstance(segment, TranscriptSegment) else segment.copy()
                video_path = self.cut_segment(i, chunk["start"], chunk["end"])
                
                if video_path:
                    chunk["video_path"] = video_path
                    processed_chunks.append(chunk)
                else:
                    failed_chunks.append(i)
                    
            except Exception as e:
                self.error_handler.log_video_error(
                    f"Failed to process chunk: {str(e)}",
                    f"chunk_{i:03d}"
                )
                failed_chunks.append(i)
                continue
                
        if failed_chunks:
            self.error_handler.log_video_error(
                f"Failed to process {len(failed_chunks)} chunks: {failed_chunks}"
            )
            
        return processed_chunks
