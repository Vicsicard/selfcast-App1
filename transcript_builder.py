#!/usr/bin/env python
"""
Transcript Builder - Main entry point
Converts video interviews into structured markdown transcripts
"""
import argparse
import json
import os
import time
from pathlib import Path
from typing import List, Dict
from loguru import logger

from utils.ffmpeg_audio import extract_audio
from utils.transcribe import Transcriber
from utils.embedding import EmbeddingGenerator
from utils.similarity import find_best_match
from utils.chunk_builder import ChunkBuilder
from utils.file_writer import FileWriter
from utils.question_loader import load_questions, QuestionLoadError
from utils.supabase_writer import SupabaseWriter

def setup_logger(output_dir: Path):
    """Configure logging to both console and file."""
    logger.add(output_dir / "errors.log", 
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               level="ERROR",
               rotation="1 week")

def embed_with_retries(embedding_gen: EmbeddingGenerator, texts: List[str], max_retries: int = 3) -> List[List[float]]:
    """Generate embeddings with exponential backoff retry."""
    embeddings = []
    batch_size = 15  # Process 15 texts at a time
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        retry_count = 0
        delay = 1  # Initial delay in seconds
        
        while retry_count < max_retries:
            try:
                batch_embeddings = [embedding_gen.generate_embedding(text) for text in batch]
                embeddings.extend(batch_embeddings)
                break
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    logger.error(f"Failed to generate embeddings after {max_retries} retries: {str(e)}")
                    raise
                logger.warning(f"Embedding attempt {retry_count} failed, retrying in {delay}s: {str(e)}")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                
    return embeddings

def main():
    parser = argparse.ArgumentParser(description="Convert video interviews to structured transcripts")
    parser.add_argument("--mp4", required=True, help="Path to input MP4 file")
    parser.add_argument("--category", required=True, 
                      choices=['narrative_defense', 'narrative_elevation', 'narrative_transition'],
                      help="Category of questions to use for this interview")
    parser.add_argument("--project-id", help="Optional project ID for Supabase")
    parser.add_argument("--user-id", help="Optional user ID for Supabase")
    args = parser.parse_args()
    
    # Setup directories
    input_path = Path(args.mp4)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    output_dir = input_path.parent / "output"
    output_dir.mkdir(exist_ok=True)
    setup_logger(output_dir)
    
    try:
        # Load combined questions for this interview
        data_dir = Path(__file__).parent / 'data'
        questions = load_questions(args.category, data_dir)
        
        # Extract audio
        logger.info("Extracting audio...")
        audio_path = output_dir / "audio.wav"
        if not extract_audio(str(input_path), str(audio_path)):
            raise RuntimeError("Audio extraction failed")
        
        # Transcribe audio
        logger.info("Transcribing audio...")
        transcriber = Transcriber(model_size="base")
        transcript = transcriber.transcribe_audio(str(audio_path))
        
        # Initialize embedding generator
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        embedding_gen = EmbeddingGenerator(api_key)
        
        # Generate embeddings for questions
        logger.info("Generating question embeddings...")
        question_texts = [q["text"] for q in questions]
        try:
            question_embeddings = embed_with_retries(embedding_gen, question_texts)
        except Exception as e:
            logger.error(f"Failed to generate question embeddings: {str(e)}")
            raise
        
        # Process transcript segments
        logger.info("Processing transcript...")
        chunk_builder = ChunkBuilder()
        
        for segment in transcript:
            if segment.speaker == "Speaker 0":  # Interviewer
                # Generate embedding for interviewer line
                try:
                    line_embedding = embedding_gen.generate_embedding(segment.text)
                    # Find best matching question
                    best_idx, score = find_best_match(line_embedding, question_embeddings)
                    if best_idx >= 0:  # Match found
                        question = questions[best_idx]
                        chunk_builder.start_new_chunk(
                            chunk_id=f"chunk_{len(chunk_builder.chunks) + 1}",
                            question_id=question["id"],
                            start_time=segment.start,
                            question_text=question["text"],
                            similarity_score=score
                        )
                except Exception as e:
                    logger.error(f"Error processing interviewer line: {str(e)}")
            else:  # Client response
                chunk_builder.add_response(segment)
        
        # Write outputs
        logger.info("Writing outputs...")
        chunks = chunk_builder.finalize_chunks()
        writer = FileWriter(str(output_dir))
        
        writer.write_transcript_chunks(chunks)
        writer.write_chunk_metadata(chunks)
        
        # Generate and write vectors
        chunk_vectors = {
            chunk.chunk_id: embedding_gen.generate_embedding(chunk.response_text)
            for chunk in chunks
        }
        writer.write_chunk_vectors(chunk_vectors)
        
        # Write to Supabase if environment variables are set
        if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
            logger.info("Writing to Supabase...")
            supabase_writer = SupabaseWriter(str(output_dir))
            success = supabase_writer.write_chunks(
                chunks=chunks,
                chunk_vectors=chunk_vectors,
                project_id=args.project_id,
                user_id=args.user_id
            )
            if success:
                logger.info("Successfully wrote all chunks to Supabase")
            else:
                logger.warning("Some chunks failed to write to Supabase. Check errors.log for details")
        
        logger.info("Processing complete!")
    except QuestionLoadError as e:
        logger.error(f"Failed to load questions: {str(e)}")
        raise

if __name__ == "__main__":
    main()
