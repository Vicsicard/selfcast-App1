"""
VTT Parser - Utility for parsing WebVTT subtitle files
"""
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger

from .models import TranscriptSegment

class VTTParser:
    """Parser for WebVTT subtitle files."""
    
    def __init__(self, vtt_path: str):
        """Initialize VTT parser with file path."""
        self.vtt_path = Path(vtt_path)
        if not self.vtt_path.exists():
            raise FileNotFoundError(f"VTT file not found: {vtt_path}")

    def _parse_timestamp(self, timestamp: str) -> float:
        """Convert VTT timestamp to seconds.
        Handles both HH:MM:SS.mmm and MM:SS.mmm formats.
        """
        try:
            # Remove any leading/trailing whitespace
            timestamp = timestamp.strip()
            
            # Split into parts
            parts = timestamp.split(':')
            
            if len(parts) == 3:  # HH:MM:SS.mmm
                hours, minutes, seconds = parts
                hours = int(hours)
                minutes = int(minutes)
            elif len(parts) == 2:  # MM:SS.mmm
                hours = 0
                minutes, seconds = parts
                minutes = int(minutes)
            else:
                raise ValueError(f"Invalid timestamp format: {timestamp}")
            
            # Handle seconds with milliseconds
            seconds = float(seconds)
            
            # Convert to total seconds
            total_seconds = (hours * 3600) + (minutes * 60) + seconds
            return round(total_seconds, 3)
            
        except Exception as e:
            logger.error(f"Failed to parse timestamp {timestamp}: {str(e)}")
            return 0.0
    
    def _parse_timing_line(self, line: str) -> Tuple[float, float]:
        """Parse VTT timing line into start and end times.
        
        Format: HH:MM:SS.mmm --> HH:MM:SS.mmm
        """
        try:
            # Split on arrow and strip whitespace
            start_str, end_str = line.split("-->")
            start_time = self._parse_timestamp(start_str.strip())
            end_time = self._parse_timestamp(end_str.strip())
            return start_time, end_time
            
        except Exception as e:
            logger.error(f"Failed to parse timing line {line}: {str(e)}")
            return 0.0, 0.0
    
    def _detect_speaker(self, text: str) -> Tuple[str, str]:
        """Detect and extract speaker from text.
        
        Common formats:
        - [Speaker Name]: Text
        - <v Speaker Name>Text
        - Speaker Name: Text
        """
        # Try bracket format [Speaker]: Text
        bracket_match = re.match(r'\[(.*?)\]:\s*(.*)', text)
        if bracket_match:
            return bracket_match.group(1), bracket_match.group(2)
            
        # Try HTML format <v Speaker>Text
        html_match = re.match(r'<v\s+(.*?)>(.*)', text)
        if html_match:
            return html_match.group(1), html_match.group(2)
            
        # Try basic format Speaker: Text
        basic_match = re.match(r'([^:]+):\s*(.*)', text)
        if basic_match:
            return basic_match.group(1), basic_match.group(2)
            
        # No speaker detected
        return "unknown", text.strip()
    
    def parse(self) -> List[TranscriptSegment]:
        """Parse VTT file and return list of segments with timestamps and text."""
        segments = []
        current_segment = None
        
        with open(self.vtt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Skip WEBVTT header
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() == 'WEBVTT':
                start_idx = i + 1
                break
        
        # Process remaining lines
        for line in lines[start_idx:]:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if line contains timestamps
            if '-->' in line:
                # Start new segment
                if current_segment:
                    segments.append(current_segment)
                
                # Parse timestamps
                start_str, end_str = line.split('-->')
                start_time = self._parse_timestamp(start_str)
                end_time = self._parse_timestamp(end_str)
                
                current_segment = TranscriptSegment(
                    start=start_time,
                    end=end_time,
                    text='',
                    speaker=''
                )
            
            # Process text content
            elif current_segment is not None:
                # Check for speaker label
                if ':' in line:
                    speaker, text = line.split(':', 1)
                    current_segment.speaker = speaker.strip()
                    current_segment.text = text.strip()
                else:
                    # Append to existing text if no speaker label
                    current_segment.text += ' ' + line if current_segment.text else line
        
        # Add final segment
        if current_segment:
            segments.append(current_segment)
        
        return segments
