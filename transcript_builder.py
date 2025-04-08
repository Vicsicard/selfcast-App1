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

# Lazy imports for Whisper mode
whisper = None
ffmpeg_audio = None

def setup_logger(output_dir: Path):
    """Configure logging to both console and file."""
    logger.add(output_dir / "errors.log", 
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               level="ERROR",
               rotation="1 week")

def process_vtt_mode(input_path: str, vtt_path: str, output_dir: str) -> List[Dict]:
    """Process interview using VTT file for timestamps."""
    try:
        print("\n[VTT MODE] Starting...")
        print(f"-> Using VTT file: {vtt_path}")
        
        # Parse VTT file
        print("-> Parsing VTT transcript...")
        parser = VTTParser(vtt_path)
        segments = parser.parse()
        
        # Process video chunks
        print(f"\n-> Cutting video segments from {input_path}")
        video_cutter = VideoCutter(input_path, output_dir)
        processed_chunks = video_cutter.process_chunks(segments)
        
        # Write output files
        print("\n-> Generating output files...")
        file_writer = FileWriter(output_dir)
        file_writer.write_transcript_chunks(processed_chunks)
        file_writer.write_chunk_metadata(processed_chunks)
        
        print("\n[SUCCESS] VTT processing complete!")
        return processed_chunks
        
    except Exception as e:
        logger.error(f"VTT processing failed: {str(e)}")
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
    parser.add_argument("--mp4", required=True, help="Path to input MP4 file")
    parser.add_argument("--vtt", help="Path to VTT transcript file (optional)")
    parser.add_argument("--category", required=True, choices=["narrative_defense", "narrative_elevation", "narrative_transition"])
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    parser.add_argument("--project-id", help="Optional project ID for Supabase")
    parser.add_argument("--user-id", help="Optional user ID for Supabase")
    parser.add_argument("--job-id", help="Optional job ID for organizing outputs")
    
    args = parser.parse_args()
    
    try:
        # Setup paths
        input_path = Path(args.mp4)
        output_dir = Path(args.output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input video not found: {args.mp4}")
            
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize FileWriter with job ID
        file_writer = FileWriter(str(output_dir), job_id=args.job_id)
        setup_logger(file_writer.job_dir)
        
        # Process based on mode
        mode = determine_processing_mode(args)
        if mode == "vtt":
            vtt_path = Path(args.vtt)
            if not vtt_path.exists():
                raise FileNotFoundError(f"VTT file not found: {args.vtt}")
            chunks = process_vtt_mode(str(input_path), str(vtt_path), str(output_dir))
        else:
            chunks = process_whisper_mode(str(input_path), str(output_dir))
        
        # Upload to Supabase if configured
        if args.project_id and args.user_id:
            logger.info("Uploading to Supabase...")
            try:
                from utils.supabase_writer import SupabaseWriter
                from utils.supabase_upload import upload_file_to_supabase
                
                supabase_writer = SupabaseWriter(args.project_id)
                
                # Upload video file
                video_url = upload_file_to_supabase(
                    str(input_path),
                    args.project_id,
                    args.user_id,
                    file_writer.job_id
                )
                
                # Write transcript data
                supabase_writer.write_transcript(
                    transcript=chunks,
                    video_url=video_url,
                    user_id=args.user_id,
                    job_id=file_writer.job_id
                )
                
            except Exception as e:
                logger.error(f"Supabase upload failed: {str(e)}")
                # Continue execution even if upload fails
        
        logger.info(f"Processing complete! Output directory: {output_dir}")
        
        return chunks
        
    except Exception as e:
        handle_app_error(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
