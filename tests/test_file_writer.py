"""Test the FileWriter markdown formatting with mock transcript data."""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class MockTranscriptChunk:
    chunk_id: str
    question_id: str
    question_text: str
    start_time: float
    end_time: float
    response_text: str
    similarity_score: float

class FileWriter:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
    def write_transcript_chunks(self, chunks: List[MockTranscriptChunk]) -> None:
        """Write transcript chunks to markdown file."""
        output_path = self.output_dir / "transcript_chunks.md"
        
        with open(output_path, "w", encoding="utf-8") as f:
            for i, chunk in enumerate(chunks):
                # Write header with question ID and label
                question_id = chunk.question_id
                question_label = "New Identity" if question_id == "NT03" else "Hidden Power"  # Mock labels
                f.write(f"## [{question_id}] {question_label}\n\n")
                
                # Write matched question
                f.write(f"**Matched Question**: {chunk.question_text}\n\n")
                
                # Write timestamp range
                start_time = self.format_timestamp(chunk.start_time)
                end_time = self.format_timestamp(chunk.end_time)
                f.write(f"**Timestamp**: {start_time} — {end_time}\n\n")
                
                # Write client responses in blockquote format
                responses = chunk.response_text.strip().split("\n")
                for response in responses:
                    if response.strip():
                        f.write(f"> Speaker 1: {response.strip()}\n")
                
                # Add empty line between chunks (except after last chunk)
                if i < len(chunks) - 1:
                    f.write("\n\n")
                
    def write_chunk_metadata(self, chunks: List[MockTranscriptChunk]) -> None:
        """Write chunk metadata to JSON file."""
        output_path = self.output_dir / "chunk_metadata.json"
        
        metadata = [{
            "chunk_id": chunk.chunk_id,
            "question_id": chunk.question_id,
            "start_time": chunk.start_time,
            "end_time": chunk.end_time,
            "similarity_score": chunk.similarity_score
        } for chunk in chunks]
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

def create_mock_chunks() -> List[MockTranscriptChunk]:
    """Create mock transcript chunks for testing."""
    return [
        MockTranscriptChunk(
            chunk_id="chunk_1",
            question_id="NT03",
            question_text="What do you want to be known for now?",
            start_time=262.5,  # 4:22.5
            end_time=430.0,    # 7:10.0
            response_text=(
                "I want to be known as someone who helps others find their voice.\n"
                "You know, for years I was afraid to speak up.\n"
                "But now I realize that my story could help others break through their own barriers."
            ),
            similarity_score=0.92
        ),
        MockTranscriptChunk(
            chunk_id="chunk_2",
            question_id="NE05",
            question_text="What part of your identity or experience have you been hesitant to share—but might actually be your power?",
            start_time=612.0,   # 10:12.0
            end_time=798.3,     # 13:18.3
            response_text=(
                "My background in psychology, actually.\n"
                "I used to think it wasn't relevant to my current work in tech.\n"
                "But it's given me this unique lens on how people interact with technology.\n"
                "It's become this unexpected strength in designing user experiences."
            ),
            similarity_score=0.88
        )
    ]

def main():
    """Test the FileWriter with mock transcript chunks."""
    # Create output directory
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Initialize FileWriter
    writer = FileWriter(str(output_dir))
    
    # Create and write mock chunks
    chunks = create_mock_chunks()
    writer.write_transcript_chunks(chunks)
    writer.write_chunk_metadata(chunks)
    
    print(f"Test transcript written to: {output_dir / 'transcript_chunks.md'}")
    print(f"Test metadata written to: {output_dir / 'chunk_metadata.json'}")

if __name__ == "__main__":
    main()
