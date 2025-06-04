#!/usr/bin/env python
"""
Transcript Builder - Process interview transcripts into structured chunks.
Supports both VTT and Whisper modes for maximum flexibility.
Updated to use MongoDB instead of Supabase for storage.
"""

import argparse
from pathlib import Path
from typing import List, Dict
from loguru import logger
import sys
from datetime import datetime
import platform
import os
import shutil

from utils.vtt_parser import VTTParser
from utils.file_writer import FileWriter
from utils.error_logger import handle_app_error
from utils.embedding import EmbeddingGenerator
from utils.mongodb_client import get_mongodb_client
from utils.verify_outputs import verify_local_outputs, verify_chunk_consistency

# Lazy imports for Whisper mode
whisper = None
ffmpeg_audio = None

def setup_logger(output_dir: Path):
    """Configure logging to both console and file."""
    logger.add(output_dir / "errors.log", 
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               level="ERROR",
               rotation="1 week")

def process_vtt_mode(input_path: str, vtt_path: str, output_dir: str, category: str, email: str = None) -> List[Dict]:
    """Process interview using VTT file for timestamps.
    
    Args:
        input_path: Optional path to input MP4 video file. Can be empty.
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
        file_writer = FileWriter(output_dir, category=category, email=email)
        job_id = file_writer.job_id
        
        processed_chunks = []
        
        # Process video chunks if MP4 provided
        if input_path:
            print(f"\n-> Cutting video segments from {input_path}")
            video_cutter = VideoCutter(input_path, output_dir, job_id=job_id)
            processed_chunks = video_cutter.process_chunks(segments)
        else:
            # Create base chunks without video
            processed_chunks = [{'id': f'chunk_{i+1:03d}', 'text': s.text, 'start': s.start, 'end': s.end} 
                              for i, s in enumerate(segments)]
        
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
        file_writer.write_chunk_metadata(processed_chunks)
        file_writer.write_chunk_vectors(processed_chunks)
        file_writer.write_video_index(processed_chunks)
        
        return processed_chunks
        
    except Exception as e:
        handle_app_error(f"VTT processing failed: {str(e)}")
        raise

def process_whisper_mode(input_path: str, output_dir: str, email: str = None) -> List[Dict]:
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
        result = model.transcribe(str(audio_path))
        
        # Process segments
        print("\n-> Processing segments...")
        processed_chunks = []
        for segment in result["segments"]:
            chunk = {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "speaker": "Speaker 2"  # Default to Speaker 2 for consistency
            }
            processed_chunks.append(chunk)
            
        # Write output files
        print("\n-> Writing output files...")
        file_writer = FileWriter(output_dir, email=email)
        file_writer.write_transcript_chunks(processed_chunks)
        file_writer.write_chunk_metadata(processed_chunks)
        file_writer.write_video_index(processed_chunks)
        
        print("\n[OK] Whisper processing complete!")
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

def verify_processing(output_dir: Path, job_id: str, has_video: bool = False, has_audio: bool = False) -> bool:
    """Verify all outputs were created and uploaded correctly.
    
    Args:
        output_dir: Path to output directory
        job_id: Job ID for Supabase verification
        has_video: Whether video files should be present
        has_audio: Whether audio files should be present
        
    Returns:
        bool: True if verification passed, False otherwise
    """
    print("\n[*] Verifying outputs...")
    
    # Get timestamped output directory
    timestamped_dirs = list(Path(output_dir).glob("*"))
    if not timestamped_dirs:
        print("[ERROR] Missing output directory")
        return False
    
    timestamped_dir = timestamped_dirs[0]  # Use first directory
    if not timestamped_dir.exists():
        print("[ERROR] Missing timestamped output directory")
        return False
        
    # Check local files
    print("\n[*] Checking local files...")
    if not verify_local_outputs(timestamped_dir, has_video, has_audio):
        print("[ERROR] Missing local files or directories")
        return False
        
    # Check Supabase storage
    print("\n[*] Checking Supabase storage...")
    if not verify_supabase_outputs(job_id, has_video, has_audio):
        print("[ERROR] Missing Supabase files")
        return False
        
    # Check chunk consistency
    print("\n[*] Checking chunk consistency...")
    consistency = verify_chunk_consistency(
        {
            "transcript_chunks.md": timestamped_dir / "transcript_chunks.md",
            "chunk_metadata.json": timestamped_dir / "chunk_metadata.json",
            "chunk_vectors.json": timestamped_dir / "chunk_vectors.json"
        },
        {"job_id": job_id}
    )
    
    for check, results in consistency.items():
        if not results["consistent"]:
            print(f"[ERROR] Chunk consistency check failed: {check}")
            print(f"Details: {results.get('details', 'No details available')}")
            return False
            
    print("\n[OK] All verifications passed!")
    return True

def verify_python_version():
    """Verify Python 3.10.x is being used."""
    version = platform.python_version()
    major, minor, _ = map(int, version.split('.'))
    
    if major != 3 or minor != 10:
        print(" ERROR: This application requires Python 3.10")
        print(f"Current version: {version}")
        print("Please switch to Python 3.10 and try again")
        sys.exit(1)
    
    print(f"[OK] Python version verified: {version}")

def verify_environment():
    """Verify venv310 environment is active."""
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    executable_path = sys.executable
    
    # Check if we're running from the venv's Python directly
    if 'venv310' in executable_path:
        print("[OK] Environment verified: venv310 (direct)")
        return
        
    # Check if venv is activated
    if not venv_path or 'venv310' not in venv_path:
        print(" ERROR: venv310 environment not active")
        print("Please activate the environment:")
        print("  ./venv310/Scripts/activate")
        sys.exit(1)
    
    print("[OK] Environment verified: venv310")

def verify_directory_structure():
    """Verify required directories exist."""
    required_dirs = {
        'docs': ['OPERATIONS.md', 'TROUBLESHOOTING.md'],
        'input': [],
        'output': [],
        'completed_transcripts': [],
        'utils': [],
        'tests': []
    }
    
    for dir_name, required_files in required_dirs.items():
        if not Path(dir_name).exists():
            print(f"ERROR: Required directory missing: {dir_name}")
            sys.exit(1)
            
        for file_name in required_files:
            if not (Path(dir_name) / file_name).exists():
                print(f"ERROR: Required file missing: {dir_name}/{file_name}")
                sys.exit(1)
    
    print("[OK] Directory structure verified")

def move_to_completed(output_dir: str, category: str) -> None:
    """Move processed files to completed_transcripts directory.
    
    Args:
        output_dir: Path to output directory
        category: Category for organizing completed transcripts
    """
    # Get timestamp for completed directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    completed_dir = Path(f"completed_transcripts/{timestamp}_{category}")
    completed_dir.mkdir(parents=True, exist_ok=True)
    
    # Get job ID and category from output dir
    job_dir = Path(output_dir)
    job_id = job_dir.name.replace("job_", "")
    
    # Find the transcript file - handle both original and email-prefixed filenames
    job_timestamp_category_dir = list(job_dir.glob(f"*_{category}"))[0]
    print(f"-> Looking for transcript files in: {job_timestamp_category_dir}")
    
    # Try to find the transcript file with any potential prefix
    transcript_files = list(job_timestamp_category_dir.glob("*transcript_chunks.md"))
    if not transcript_files:
        # Try without underscore
        transcript_files = list(job_timestamp_category_dir.glob("*transcript*.md"))
    
    if not transcript_files:
        raise FileNotFoundError(f"No transcript files found in: {job_timestamp_category_dir}")
    
    # Use the first matching file
    source_file = transcript_files[0]
    print(f"-> Found transcript file: {source_file}")
    
    # Also grab the metadata file
    metadata_files = list(job_timestamp_category_dir.glob("*chunk_metadata.json"))
    
    # Copy transcript to completed directory (keep original name)
    target_file = completed_dir / source_file.name
    shutil.copy2(source_file, target_file)
    print(f"-> Copied transcript to: {target_file}")
    
    # Copy metadata if found
    if metadata_files:
        metadata_source = metadata_files[0]
        metadata_target = completed_dir / metadata_source.name
        shutil.copy2(metadata_source, metadata_target)
        print(f"-> Copied metadata to: {metadata_target}")
    
    logger.info(f"Moved transcript to {target_file}")

def main():
    """Main entry point for transcript builder."""
    # Verify Python version and environment first
    verify_python_version()
    verify_environment()
    verify_directory_structure()
    
    parser = argparse.ArgumentParser(description="Process interview videos into transcript chunks.")
    parser.add_argument("--mp4", required=False, help="Optional: Path to input MP4 video file")
    parser.add_argument("--vtt", required=False, help="Optional: Path to input VTT subtitle file")
    parser.add_argument("--m4a", required=False, help="Optional: Path to input M4A audio file")
    parser.add_argument("--category", required=True, help="Category for organizing output")
    parser.add_argument("--email", required=False, help="Client email for project identification")
    parser.add_argument("--output", default="output", help="Output directory path")
    
    args = parser.parse_args()
    
    # Validate input files
    mp4_path = None
    if args.mp4:
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

    # Verify at least one input file is provided
    if not any([mp4_path, vtt_path, m4a_path]):
        handle_app_error("At least one input file (MP4, VTT, or M4A) must be provided")
        sys.exit(1)
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"job_{timestamp}"
    output_dir = Path(args.output) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logger(output_dir)
    
    try:
        print("\n Starting Transcript Builder")
        print(f"-> Input video: {mp4_path}" if mp4_path else "")
        print(f"-> Input VTT: {vtt_path}" if vtt_path else "")
        print(f"-> Input M4A: {m4a_path}" if m4a_path else "")
        print(f"-> Category: {args.category}")
        print(f"-> Client email: {args.email}" if args.email else "No client email provided")
        print(f"-> Output directory: {output_dir}\n")
        
        # Determine and execute processing mode
        if vtt_path:
            # VTT mode - use provided subtitle file
            chunks = process_vtt_mode(str(mp4_path) if mp4_path else "", str(vtt_path), str(output_dir), args.category, args.email, str(m4a_path) if m4a_path else None)
        else:
            # Whisper mode - transcribe from audio
            input_path = str(m4a_path) if m4a_path else str(mp4_path)
            chunks = process_whisper_mode(input_path, str(output_dir), args.email)
        
        # Verify all outputs
        verification_result = verify_processing(output_dir, job_id, has_video=bool(mp4_path), has_audio=bool(m4a_path))
        if not verification_result:
            # Just log the error but continue with processing
            # This allows us to continue even if Supabase verification fails
            handle_app_error("Some verification steps failed - continuing anyway")
            print("\n[WARNING] Some verification steps failed, but continuing with processing")
            
        # Move transcript to completed_transcripts
        move_to_completed(output_dir, args.category)
            
        print("\n Processing complete!")
        print(f"-> Generated {len(chunks)} chunks")
        print(f"-> Output saved to: {output_dir}")
        print(f"-> Transcript moved to: completed_transcripts/{output_dir.name}_{args.category}")
        
    except Exception as e:
        handle_app_error(f"Processing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
