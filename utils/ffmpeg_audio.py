"""
FFmpeg Audio Utility - Extract audio from video files
"""
import os
from pathlib import Path
import subprocess
from loguru import logger

def extract_audio(input_path: Path, output_dir: Path) -> Path:
    """Extract audio from video file using FFmpeg.
    
    Args:
        input_path: Path to input video file
        output_dir: Directory to save extracted audio
        
    Returns:
        Path to extracted audio file
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set output path
        output_path = output_dir / "audio.wav"
        
        # Build FFmpeg command
        command = [
            "ffmpeg",
            "-i", str(input_path),
            "-vn",                  # Disable video
            "-acodec", "pcm_s16le", # Use PCM 16-bit encoding
            "-ar", "16000",         # Set sample rate to 16kHz
            "-ac", "1",             # Convert to mono
            "-y",                   # Overwrite output
            str(output_path)
        ]
        
        # Run FFmpeg
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise RuntimeError(f"Audio extraction failed: {result.stderr}")
            
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to extract audio: {str(e)}")
        raise
