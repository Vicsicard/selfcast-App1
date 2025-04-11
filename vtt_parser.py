"""
VTT Parser - Utility for parsing WebVTT files and extracting timestamps and text
"""
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import re
from datetime import datetime
from loguru import logger

class VTTChunk:
    def __init__(self, start_time: float, end_time: float, text: str, speaker: Optional[str] = None):
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.speaker = speaker
        self.question: Optional[str] = None
        self.similarity: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert chunk to dictionary format matching transcript_chunks.md structure."""
        return {
            "start": self.start_time,
            "end": self.end_time,
            "text": self.text,
            "speaker": self.speaker,
            "question": self.question,
            "similarity": self.similarity
        }

    def duration(self) -> float:
        """Get chunk duration in seconds."""
        return self.end_time - self.start_time

class VTTParser:
    def __init__(self, vtt_path: Path, max_chunk_duration: float = 45.0):
        """Initialize VTT parser.
        
        Args:
            vtt_path: Path to VTT file
            max_chunk_duration: Maximum duration in seconds for a single chunk
        """
        self.vtt_path = vtt_path
        self.max_chunk_duration = max_chunk_duration
        self.chunks: List[VTTChunk] = []
        self.current_speaker: Optional[str] = None

    def _parse_timestamp(self, timestamp: str) -> float:
        """Convert VTT timestamp (HH:MM:SS.mmm) to seconds."""
        try:
            time_obj = datetime.strptime(timestamp.strip(), "%H:%M:%S.%f")
            return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1000000
        except ValueError as e:
            logger.error(f"Failed to parse timestamp {timestamp}: {str(e)}")
            return 0.0

    def _extract_speaker(self, text: str) -> Tuple[str, str]:
        """Extract speaker name and clean text from VTT cue."""
        # Common VTT speaker patterns
        patterns = [
            r"^<v\s+([^>]+)>(.+)$",  # <v Speaker>Text
            r"^([^:]+):\s*(.+)$",     # Speaker: Text
            r"^\[([^\]]+)\]\s*(.+)$", # [Speaker] Text
            r"^\(([^\)]+)\)\s*(.+)$"  # (Speaker) Text
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text.strip())
            if match:
                return match.group(1).strip(), match.group(2).strip()
        
        # If no speaker pattern found, use current speaker
        return self.current_speaker or "Unknown", text.strip()

    def _should_start_new_chunk(self, current_chunk: VTTChunk, next_chunk: VTTChunk) -> bool:
        """Determine if we should start a new chunk based on speaker or duration."""
        if not current_chunk:
            return True
            
        # Start new chunk if speaker changes
        if current_chunk.speaker != next_chunk.speaker:
            return True
            
        # Start new chunk if max duration exceeded
        current_duration = current_chunk.duration()
        if current_duration >= self.max_chunk_duration:
            return True
            
        # Start new chunk if there's a long pause (> 2 seconds)
        if next_chunk.start_time - current_chunk.end_time > 2.0:
            return True
            
        return False

    def parse(self) -> List[VTTChunk]:
        """Parse VTT file and return list of chunks with timestamps and text."""
        if not self.vtt_path.exists():
            raise FileNotFoundError(f"VTT file not found: {self.vtt_path}")

        with open(self.vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into cues (skip WebVTT header)
        cues = content.split('\n\n')[1:]
        raw_chunks: List[VTTChunk] = []
        
        for cue in cues:
            lines = cue.strip().split('\n')
            if len(lines) < 2:
                continue

            # Parse timestamp line (00:00:00.000 --> 00:00:00.000)
            timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', lines[1])
            if not timestamp_match:
                continue

            start_time = self._parse_timestamp(timestamp_match.group(1))
            end_time = self._parse_timestamp(timestamp_match.group(2))
            
            # Combine remaining lines as text
            text = ' '.join(lines[2:])
            speaker, clean_text = self._extract_speaker(text)
            self.current_speaker = speaker  # Update current speaker
            
            raw_chunks.append(VTTChunk(start_time, end_time, clean_text, speaker))

        # Group chunks by speaker and duration
        self.chunks = self._group_chunks(raw_chunks)
        return self.chunks

    def _group_chunks(self, raw_chunks: List[VTTChunk]) -> List[VTTChunk]:
        """Group raw chunks by speaker and duration limits."""
        grouped_chunks: List[VTTChunk] = []
        current_chunk: Optional[VTTChunk] = None
        
        for chunk in raw_chunks:
            if not current_chunk or self._should_start_new_chunk(current_chunk, chunk):
                # Start new chunk
                if current_chunk:
                    grouped_chunks.append(current_chunk)
                current_chunk = chunk
            else:
                # Extend current chunk
                current_chunk.end_time = chunk.end_time
                current_chunk.text += " " + chunk.text
        
        # Add last chunk
        if current_chunk:
            grouped_chunks.append(current_chunk)
        
        return grouped_chunks

    def get_chunks(self) -> List[Dict]:
        """Get chunks in format compatible with transcript_chunks.md."""
        if not self.chunks:
            self.parse()
        
        return [chunk.to_dict() for chunk in self.chunks]

    def write_transcript(self, output_dir: Path) -> None:
        """Write transcript chunks to markdown and JSON files."""
        if not self.chunks:
            self.parse()
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write transcript_chunks.md
        with open(output_dir / "transcript_chunks.md", "w", encoding="utf-8") as f:
            for i, chunk in enumerate(self.chunks, 1):
                f.write(f"## Chunk {i}\n\n")
                if chunk.question:
                    f.write(f"**Question:** {chunk.question}\n\n")
                f.write(f"**Response:** {chunk.text}\n\n")
                f.write(f"*Speaker: {chunk.speaker}*\n\n")
                f.write("---\n\n")
        
        # Write chunk_metadata.json
        metadata = {
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "total_chunks": len(self.chunks),
            "source_file": str(self.vtt_path)
        }
        
        with open(output_dir / "chunk_metadata.json", "w", encoding="utf-8") as f:
            import json
            json.dump(metadata, f, indent=2)
