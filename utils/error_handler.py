"""
Error handling utilities for transcript processing.
"""
from enum import Enum
from pathlib import Path
from typing import Optional
from datetime import datetime
from loguru import logger

class ErrorType(Enum):
    """Types of errors that can occur during processing."""
    VTT_PARSE = "VTT Parse Error"
    MISSING_SPEAKER = "Missing Speaker Tag"
    VIDEO_SLICE = "Video Slice Error"
    EMBEDDING = "Embedding Generation Error"
    GENERAL = "General Error"

class ErrorHandler:
    """Centralized error handling for transcript processing."""
    
    def __init__(self, output_dir: Path):
        """Initialize error handler with output directory.
        
        Args:
            output_dir: Directory containing errors.log
        """
        self.log_file = output_dir / "errors.log"
        self._ensure_log_file()
        
    def _ensure_log_file(self) -> None:
        """Create errors.log if it doesn't exist."""
        if not self.log_file.exists():
            self.log_file.touch()
            
    def _format_error(self, error_type: ErrorType, message: str, 
                     chunk_id: Optional[str] = None) -> str:
        """Format error message with timestamp and details."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chunk_info = f" [Chunk: {chunk_id}]" if chunk_id else ""
        return f"[{timestamp}] {error_type.value}{chunk_info}: {message}\n"
        
    def log_error(self, error_type: ErrorType, message: str, 
                  chunk_id: Optional[str] = None) -> None:
        """Log an error to errors.log.
        
        Args:
            error_type: Type of error from ErrorType enum
            message: Error message
            chunk_id: Optional chunk ID if error is chunk-specific
        """
        try:
            error_msg = self._format_error(error_type, message, chunk_id)
            
            # Log to file
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(error_msg)
                
            # Also log to console
            logger.error(error_msg.strip())
            
        except Exception as e:
            # If we can't write to error log, at least log to console
            logger.error(f"Failed to write to error log: {str(e)}")
            logger.error(f"Original error: {error_type.value} - {message}")
            
    def log_vtt_error(self, message: str, chunk_id: Optional[str] = None) -> None:
        """Log a VTT parsing error."""
        self.log_error(ErrorType.VTT_PARSE, message, chunk_id)
        
    def log_speaker_error(self, message: str, chunk_id: Optional[str] = None) -> None:
        """Log a missing speaker tag error."""
        self.log_error(ErrorType.MISSING_SPEAKER, message, chunk_id)
        
    def log_video_error(self, message: str, chunk_id: Optional[str] = None) -> None:
        """Log a video slicing error."""
        self.log_error(ErrorType.VIDEO_SLICE, message, chunk_id)
        
    def log_embedding_error(self, message: str, chunk_id: Optional[str] = None) -> None:
        """Log an embedding generation error."""
        self.log_error(ErrorType.EMBEDDING, message, chunk_id)
        
    def get_error_count(self) -> int:
        """Get total number of errors logged."""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
