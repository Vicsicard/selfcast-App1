#!/usr/bin/env python
"""
Webhook Transcript Processor - Simplified version of transcript_builder for webhook use
Processes VTT transcripts into structured chunks for MongoDB storage
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from loguru import logger

# Set up logging
os.makedirs("logs", exist_ok=True)
logger.add("logs/webhook_processor.log", rotation="1 day", level="INFO")

class VTTParser:
    """Parse VTT files into structured segments."""
    
    def __init__(self):
        """Initialize VTT parser."""
        self.segments = []
    
    def parse(self, vtt_path: str) -> List[Dict]:
        """Parse VTT file into segments.
        
        Args:
            vtt_path: Path to VTT file
            
        Returns:
            List of segments with timestamps and text
        """
        try:
            with open(vtt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Split by double newline (segment separator)
            raw_segments = content.split('\n\n')
            
            # Skip WEBVTT header
            if raw_segments[0].strip() == 'WEBVTT':
                raw_segments = raw_segments[1:]
                
            segments = []
            
            for i, segment in enumerate(raw_segments):
                if not segment.strip():
                    continue
                    
                lines = segment.strip().split('\n')
                
                # Need at least timestamp and text
                if len(lines) < 2:
                    continue
                    
                # Parse timestamp line
                timestamp_line = lines[0]
                if '-->' not in timestamp_line:
                    continue
                    
                start_time, end_time = timestamp_line.split('-->')
                start_time = start_time.strip()
                end_time = end_time.strip()
                
                # Parse text (may be multiple lines)
                text_lines = lines[1:]
                text = ' '.join(text_lines)
                
                # Extract speaker if present (format: "Speaker X: Text")
                speaker = None
                if ': ' in text:
                    parts = text.split(': ', 1)
                    if len(parts) == 2:
                        speaker_text, text = parts
                        # Check if it's a recognized speaker format
                        if speaker_text.lower().startswith('speaker ') or speaker_text == 'Rich Cherry':
                            speaker = speaker_text
                            
                            # Map "Rich Cherry" to "Speaker 2" for consistency
                            if speaker == 'Rich Cherry':
                                speaker = 'Speaker 2'
                
                # Create segment
                segment_data = {
                    'id': i,
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': text,
                    'speaker': speaker
                }
                
                segments.append(segment_data)
                
            self.segments = segments
            logger.info(f"Parsed {len(segments)} segments from VTT file")
            return segments
            
        except Exception as e:
            logger.error(f"Error parsing VTT file: {str(e)}")
            return []

def process_segments_into_chunks(segments: List[Dict], chunk_size: int = 3) -> List[Dict]:
    """Process segments into larger chunks for better context.
    
    Args:
        segments: List of transcript segments
        chunk_size: Number of segments per chunk
        
    Returns:
        List of chunks with combined text and metadata
    """
    chunks = []
    
    # Group segments into chunks
    for i in range(0, len(segments), chunk_size):
        chunk_segments = segments[i:i+chunk_size]
        
        # Skip empty chunks
        if not chunk_segments:
            continue
            
        # Combine text from all segments in chunk
        combined_text = ' '.join([s['text'] for s in chunk_segments])
        
        # Get start and end times
        start_time = chunk_segments[0]['start_time']
        end_time = chunk_segments[-1]['end_time']
        
        # Create chunk
        chunk = {
            'chunk_id': str(uuid.uuid4()),
            'start_time': start_time,
            'end_time': end_time,
            'text': combined_text,
            'segment_ids': [s['id'] for s in chunk_segments],
            'segment_count': len(chunk_segments),
            'speakers': list(set([s['speaker'] for s in chunk_segments if s['speaker']])),
            'created_at': datetime.now().isoformat()
        }
        
        chunks.append(chunk)
        
    logger.info(f"Created {len(chunks)} chunks from {len(segments)} segments")
    return chunks

def process_vtt(vtt_path: str, email: Optional[str] = None) -> List[Dict]:
    """Process VTT file into chunks.
    
    Args:
        vtt_path: Path to VTT file
        email: Optional email for identification
        
    Returns:
        List of processed chunks
    """
    try:
        # Parse VTT file
        parser = VTTParser()
        segments = parser.parse(vtt_path)
        
        if not segments:
            logger.error("No segments found in VTT file")
            return []
            
        # Process segments into chunks
        chunks = process_segments_into_chunks(segments)
        
        # Add email to chunks if provided
        if email:
            for chunk in chunks:
                chunk['email'] = email
                
        return chunks
        
    except Exception as e:
        logger.error(f"Error processing VTT file: {str(e)}")
        return []

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process VTT file into chunks")
    parser.add_argument("--vtt", required=True, help="Path to VTT file")
    parser.add_argument("--email", help="Email for identification")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    chunks = process_vtt(args.vtt, args.email)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2)
        print(f"Wrote {len(chunks)} chunks to {args.output}")
    else:
        print(json.dumps(chunks, indent=2))
