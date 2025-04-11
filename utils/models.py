"""
Shared data models for transcript processing.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import copy

@dataclass
class TranscriptSegment:
    """A single segment of transcribed text with timing and speaker info."""
    start: float
    end: float
    speaker: str
    text: str
    
    def get(self, key: str, default=None):
        """Dictionary-like get method for compatibility."""
        if key == "start":
            return self.start
        elif key == "end":
            return self.end
        elif key == "speaker":
            return self.speaker
        elif key == "text":
            return self.text
        return default
    
    def copy(self):
        """Create a deep copy of the segment."""
        return copy.deepcopy(self)
    
    def to_dict(self) -> Dict:
        """Convert segment to dictionary format."""
        return {
            "start": self.start,
            "end": self.end,
            "speaker": self.speaker,
            "text": self.text
        }

@dataclass
class TranscriptChunk:
    """A chunk of transcript text, typically a Q&A pair."""
    chunk_id: str
    question_id: str
    start_time: float
    end_time: float
    question_text: str
    response_text: str
    similarity_score: float = 0.0

    def to_dict(self) -> Dict:
        """Convert chunk to dictionary format."""
        return {
            "chunk_id": self.chunk_id,
            "question_id": self.question_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "question_text": self.question_text,
            "response_text": self.response_text,
            "similarity_score": self.similarity_score
        }
