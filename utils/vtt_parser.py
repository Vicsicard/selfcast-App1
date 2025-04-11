"""
VTT parsing utilities with robust error handling.
"""
from typing import List, Optional
from pathlib import Path
from loguru import logger

from .models import TranscriptSegment
from .error_handler import ErrorHandler, ErrorType

class VTTParser:
    """Parses VTT files with error handling for missing speakers and parse failures."""
    
    def __init__(self, vtt_path: str, output_dir: Path):
        """Initialize VTT parser with error handling.
        
        Args:
            vtt_path: Path to VTT file
            output_dir: Output directory for error logging
        """
        self.vtt_path = Path(vtt_path)
        self.error_handler = ErrorHandler(output_dir)
        
    def _is_speaker_2(self, speaker: Optional[str]) -> bool:
        """Check if speaker tag indicates Speaker 2."""
        if not speaker:
            return False
        return "annie sicard" in speaker.lower()  # Updated to match our specific Speaker 2
        
    def _parse_timestamp(self, timestamp: str) -> float:
        """Convert VTT timestamp to seconds.
        
        Example formats:
        - 00:00:14.920 (HH:MM:SS.mmm)
        - 00:14.920 (MM:SS.mmm)
        """
        try:
            parts = timestamp.split(":")
            if len(parts) == 3:  # HH:MM:SS.mmm
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:  # MM:SS.mmm
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                raise ValueError(f"Invalid timestamp format: {timestamp}")
        except Exception as e:
            raise ValueError(f"Failed to parse timestamp {timestamp}: {str(e)}")
        
    def _extract_speaker(self, line: str) -> Optional[str]:
        """Extract speaker tag from line with error handling."""
        try:
            if ":" not in line:
                return None
                
            speaker = line.split(":")[0].strip()
            if not speaker:
                self.error_handler.log_speaker_error(
                    f"Empty speaker tag in line: {line}"
                )
                return None
                
            return speaker
            
        except Exception as e:
            self.error_handler.log_speaker_error(
                f"Failed to extract speaker from line: {line}, Error: {str(e)}"
            )
            return None
            
    def parse_speaker_2_only(self) -> List[TranscriptSegment]:
        """Parse VTT file and extract only Speaker 2 segments.
        
        Returns:
            List of TranscriptSegment objects for Speaker 2
        """
        segments = []
        current_segment = None
        
        try:
            with open(self.vtt_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                try:
                    line = line.strip()
                    if not line or line == "WEBVTT":
                        continue
                        
                    # Try to parse timestamp line
                    if "-->" in line:
                        try:
                            start_str, end_str = line.split("-->")
                            start = self._parse_timestamp(start_str.strip())
                            end = self._parse_timestamp(end_str.strip())
                            current_segment = TranscriptSegment(
                                start=start,
                                end=end,
                                speaker="",
                                text=""
                            )
                        except Exception as e:
                            self.error_handler.log_vtt_error(
                                f"Invalid timestamp format at line {i}: {line}",
                                f"line_{i}"
                            )
                            current_segment = None
                        continue
                        
                    # Try to parse speaker and text
                    if current_segment:
                        speaker = self._extract_speaker(line)
                        if speaker:
                            if self._is_speaker_2(speaker):
                                current_segment.speaker = speaker
                                current_segment.text = line.split(":", 1)[1].strip()
                                segments.append(current_segment)
                            current_segment = None
                            
                except Exception as e:
                    self.error_handler.log_vtt_error(
                        f"Failed to parse line {i}: {line}, Error: {str(e)}",
                        f"line_{i}"
                    )
                    current_segment = None
                    continue
                    
        except Exception as e:
            self.error_handler.log_vtt_error(
                f"Failed to parse VTT file: {str(e)}"
            )
            
        return segments
