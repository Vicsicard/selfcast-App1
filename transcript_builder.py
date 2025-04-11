#!/usr/bin/env python
"""
Transcript Builder - Process interview videos into transcript chunks and video segments.
Supports both VTT and Whisper modes for maximum flexibility.
"""

import argparse
from pathlib import Path
from typing import List, Dict
from loguru import logger
import sys

from utils.vtt_parser import VTTParser
from utils.video_cutter import VideoCutter
from utils.file_writer import FileWriter
from utils.error_logger import handle_app_error
from utils.supabase_upload import upload_file_to_supabase
from utils.embedding import EmbeddingGenerator
from utils.supabase_client import get_client
from utils.audio_cutter import AudioCutter  # New import

# Lazy imports for Whisper mode
whisper = None
ffmpeg_audio = None

def setup_logger(output_dir: Path):
    """Configure logging to both console and file."""
    logger.add(output_dir / "errors.log", 
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               level="ERROR",
               rotation="1 week")

def process_vtt_mode(input_path: str, vtt_path: str, output_dir: str, category: str, m4a_path: str = None) -> List[Dict]:
    """Process interview using VTT file for timestamps.
    
    Args:
        input_path: Path to input MP4 video file
        vtt_path: Path to VTT subtitle file
        output_dir: Output directory path
        category: Category for organizing output
        m4a_path: Optional path to M4A audio file
    
    Returns:
        List of processed chunks with metadata
    """
    try:
        print("\n[VTT MODE] Starting...")
        print(f"-> Using VTT file: {vtt_path}")
        
        # Parse VTT file - extract Speaker 2 only
        print("-> Parsing VTT transcript (Speaker 2 only)...")
        parser = VTTParser(vtt_path, Path(output_dir))
        segments = parser.parse_speaker_2_only()
        
        if not segments:
            raise ValueError("No Speaker 2 segments found in VTT file")
            
        print(f"-> Found {len(segments)} Speaker 2 segments")
        
        # Initialize FileWriter
        file_writer = FileWriter(output_dir, category=category)
        job_id = file_writer.job_id
        
        # Process video chunks
        print(f"\n-> Cutting video segments from {input_path}")
        video_cutter = VideoCutter(input_path, output_dir, job_id=job_id)
        processed_chunks = video_cutter.process_chunks(segments)
        
        # Process audio chunks if m4a provided
        if m4a_path:
            print(f"\n-> Extracting audio segments from {m4a_path}")
            audio_cutter = AudioCutter(m4a_path, output_dir, job_id=job_id)
            audio_chunks = audio_cutter.process_chunks(segments)
            
            # Add audio paths to processed chunks
            for chunk, audio in zip(processed_chunks, audio_chunks):
                chunk['audio_path'] = audio['audio_path']
        
        # Generate chunk vectors (embeddings)
        print("\n-> Generating chunk embeddings...")
        embedding_gen = EmbeddingGenerator()
        processed_chunks = embedding_gen.process_chunks(processed_chunks, Path(output_dir) / job_id)
        
        # Write outputs
        print("\n-> Writing output files...")
        file_writer.write_transcript_chunks(processed_chunks)
        file_writer.write_video_index(processed_chunks)
        
        return processed_chunks
        
    except Exception as e:
        handle_app_error(f"VTT processing failed: {str(e)}")
        raise

def process_whisper_mode(input_path: str, output_dir: str) -> List[Dict]:
    """Process interview using Whisper for transcription."""
    try:
        print("\n[WHISPER MODE] Starting...")
        
        # Lazy load Whisper dependencies
        global whisper, ffmpeg_audio
        if whisper is None:
            print("-> Loading Whisper model...")
            import whisper
            from utils import ffmpeg_audio
        
        # Extract audio
        print(f"-> Extracting audio from {input_path}")
        audio_path = ffmpeg_audio.extract_audio(input_path, output_dir)
        
        # Transcribe with Whisper
        print("\n-> Transcribing with Whisper (this may take a while)...")
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        
        # Process segments
        print("\n-> Processing video segments...")
        video_cutter = VideoCutter(input_path, output_dir)
        processed_chunks = video_cutter.process_chunks(result["segments"])
        
        # Write output files
        print("\n-> Generating output files...")
        file_writer = FileWriter(output_dir)
        file_writer.write_transcript_chunks(processed_chunks)
        file_writer.write_chunk_metadata(processed_chunks)
        
        print("\n[SUCCESS] Whisper processing complete!")
        return processed_chunks
        
    except Exception as e:
        logger.error(f"Whisper processing failed: {str(e)}")
        raise

def determine_processing_mode(args) -> str:
    """Determine which processing mode to use based on input args."""
    if args.vtt:
        logger.info("VTT file provided - using VTT mode")
        return "vtt"
    else:
        logger.info("No VTT file - using Whisper mode")
        return "whisper"

def main():
    """Main entry point for transcript builder."""
    parser = argparse.ArgumentParser(description="Process interview videos into transcript chunks.")
    parser.add_argument("--mp4", required=True, help="Path to input MP4 video file")
    parser.add_argument("--vtt", required=False, help="Optional: Path to input VTT subtitle file")
    parser.add_argument("--m4a", required=False, help="Optional: Path to input M4A audio file")
    parser.add_argument("--category", required=True, help="Category for organizing output")
    parser.add_argument("--output", default="output", help="Output directory path")
    
    args = parser.parse_args()
    
    # Validate input files
    mp4_path = Path(args.mp4)
    if not mp4_path.exists():
        handle_app_error(f"MP4 file not found: {mp4_path}")
        sys.exit(1)
        
    vtt_path = None
    if args.vtt:
        vtt_path = Path(args.vtt)
        if not vtt_path.exists():
            handle_app_error(f"VTT file not found: {vtt_path}")
            sys.exit(1)
            
    m4a_path = None
    if args.m4a:
        m4a_path = Path(args.m4a)
        if not m4a_path.exists():
            handle_app_error(f"M4A file not found: {m4a_path}")
            sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logger(output_dir)
    
    try:
        print("\n Starting Transcript Builder")
        print(f"-> Input video: {mp4_path}")
        if vtt_path:
            print(f"-> Input VTT: {vtt_path}")
        if m4a_path:
            print(f"-> Input M4A: {m4a_path}")
        print(f"-> Category: {args.category}")
        print(f"-> Output directory: {output_dir}\n")
        
        # Determine and execute processing mode
        if vtt_path:
            # VTT mode - use provided subtitle file
            chunks = process_vtt_mode(str(mp4_path), str(vtt_path), str(output_dir), args.category, str(m4a_path) if m4a_path else None)
        else:
            # Whisper mode - transcribe from video
            chunks = process_whisper_mode(str(mp4_path), str(output_dir))
            
        print("\n Processing complete!")
        print(f"-> Generated {len(chunks)} chunks")
        print(f"-> Output saved to: {output_dir}")
        
    except Exception as e:
        handle_app_error(f"Processing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
