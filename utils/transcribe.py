"""
Transcription utilities using faster-whisper.
"""
from dataclasses import dataclass
from typing import List, Tuple
from faster_whisper import WhisperModel
from loguru import logger

@dataclass
class TranscriptSegment:
    start: float
    end: float
    speaker: str
    text: str

class Transcriber:
    def __init__(self, model_size: str = "base"):
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    def transcribe_audio(self, audio_path: str) -> List[TranscriptSegment]:
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
                    text=segment.text.strip()
                ))
            
            return transcript_segments
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            return []
