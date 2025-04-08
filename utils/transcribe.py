"""
Transcription utilities using faster-whisper.
"""
from typing import List, Optional, Tuple
from loguru import logger

from .models import TranscriptSegment

class Transcriber:
    def __init__(self, model_size: str = "base"):
        # Lazy import of Whisper
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        except ImportError:
            logger.error("faster-whisper not installed. Please install with: pip install faster-whisper")
            raise
    
    def transcribe(self, audio_path: str) -> List[TranscriptSegment]:
        """
        Transcribe audio file with speaker diarization.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of TranscriptSegment objects
        """
        try:
            segments, _ = self.model.transcribe(
                audio_path,
                word_timestamps=True,
                initial_prompt="This is an interview with two speakers."
            )
            
            transcript_segments = []
            current_speaker = None
            
            for segment in segments:
                # Assign speaker based on segment characteristics
                # In a real interview, we can use more sophisticated speaker detection
                if not current_speaker:
                    current_speaker = "interviewer"
                else:
                    current_speaker = "client" if current_speaker == "interviewer" else "interviewer"
                
                transcript_segments.append(TranscriptSegment(
                    start=segment.start,
                    end=segment.end,
                    speaker=current_speaker,
                    text=segment.text
                ))
            
            return transcript_segments
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise
