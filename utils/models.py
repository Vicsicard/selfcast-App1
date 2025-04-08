"""
Shared data models for transcript processing.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class TranscriptSegment:
    """A single segment of transcribed text with timing and speaker info."""
    start: float
    end: float
    speaker: str
    text: str

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
