"""
Transcript chunk building utilities.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from .transcribe import TranscriptSegment

@dataclass
class TranscriptChunk:
    chunk_id: str
    question_id: str
    start_time: float
    end_time: float
    question_text: str
    response_text: str
    similarity_score: float

class ChunkBuilder:
    def __init__(self):
        self.current_chunk: Optional[TranscriptChunk] = None
        self.chunks: List[TranscriptChunk] = []
        
    def start_new_chunk(
        self,
        chunk_id: str,
        question_id: str,
        start_time: float,
        question_text: str,
        similarity_score: float
    ):
        """Start a new chunk when an interviewer question is matched."""
        if self.current_chunk:
            self.chunks.append(self.current_chunk)
            
        self.current_chunk = TranscriptChunk(
            chunk_id=chunk_id,
            question_id=question_id,
            start_time=start_time,
            end_time=start_time,  # Will be updated when chunk ends
            question_text=question_text,
            response_text="",
            similarity_score=similarity_score
        )
    
    def add_response(self, segment: TranscriptSegment):
        """Add a client response to the current chunk."""
        if not self.current_chunk or segment.speaker == "Speaker 0":  # Skip interviewer responses
            return
            
        if self.current_chunk.response_text:
            self.current_chunk.response_text += "\n\n"
        self.current_chunk.response_text += f"Speaker {segment.speaker}: {segment.text}"
        self.current_chunk.end_time = segment.end
    
    def finalize_chunks(self) -> List[TranscriptChunk]:
        """Finalize and return all chunks."""
        if self.current_chunk:
            self.chunks.append(self.current_chunk)
            self.current_chunk = None
        return [chunk for chunk in self.chunks if chunk.response_text.strip()]  # Only return chunks with responses
