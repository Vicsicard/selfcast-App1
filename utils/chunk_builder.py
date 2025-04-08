"""
Transcript chunk building utilities.
"""
from typing import List, Dict, Optional
from loguru import logger

from .models import TranscriptSegment, TranscriptChunk

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
        similarity_score: float = 0.0
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
        if not self.current_chunk or segment.speaker == "interviewer":
            return
            
        if self.current_chunk.response_text:
            self.current_chunk.response_text += "\n\n"
        self.current_chunk.response_text += segment.text.strip()
        self.current_chunk.end_time = segment.end
    
    def build_chunks(self, segments: List[TranscriptSegment]) -> List[Dict]:
        """
        Build chunks from a list of transcript segments.
        
        Args:
            segments: List of TranscriptSegment objects
            
        Returns:
            List of chunk dictionaries
        """
        chunk_id = 1
        current_question = ""
        
        for segment in segments:
            if segment.speaker == "interviewer":
                # Start new chunk for interviewer questions
                current_question = segment.text.strip()
                self.start_new_chunk(
                    chunk_id=f"chunk_{chunk_id}",
                    question_id=f"q{chunk_id}",
                    start_time=segment.start,
                    question_text=current_question
                )
                chunk_id += 1
            else:
                # Add client responses to current chunk
                self.add_response(segment)
        
        # Add final chunk if exists
        if self.current_chunk:
            self.chunks.append(self.current_chunk)
        
        # Convert chunks to dictionaries
        return [chunk.to_dict() for chunk in self.chunks]
