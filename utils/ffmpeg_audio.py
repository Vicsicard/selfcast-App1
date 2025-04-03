"""
Audio extraction utilities using ffmpeg.
"""
import ffmpeg
import os
from loguru import logger

def extract_audio(input_path: str, output_path: str) -> bool:
    """
    Extract audio from video file using ffmpeg.
    
    Args:
        input_path: Path to input video file
        output_path: Path to output audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le', ac=1, ar='16k')
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
        return True
    except ffmpeg.Error as e:
        logger.error(f"Error extracting audio: {e.stderr.decode()}")
        return False
