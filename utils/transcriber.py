"""
Transcriber - Utility for transcribing audio using Whisper
"""
from pathlib import Path
from typing import List, Dict, Optional
import torch
import whisper
from loguru import logger

class Transcriber:
    """Handles audio transcription using Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """Initialize Whisper transcriber.
        
        Args:
            model_name: Name of Whisper model to use (tiny, base, small, medium, large)
        """
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = whisper.load_model(model_name).to(self.device)
            logger.info(f"Loaded Whisper model {model_name} on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise
            
    def transcribe(self, audio_path: Path) -> List[Dict]:
        """Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of transcript chunks with timestamps
        """
        try:
            # Load and transcribe audio
            result = self.model.transcribe(str(audio_path))
            
            # Convert segments to chunks
            chunks = []
            for segment in result["segments"]:
                chunk = {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "speaker": None  # Whisper doesn't do speaker diarization
                }
                chunks.append(chunk)
                
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {str(e)}")
            raise
