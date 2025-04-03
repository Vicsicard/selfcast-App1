"""
Supabase Writer Module

Handles writing transcript chunks and their vector embeddings to Supabase:
- Connects to Supabase using environment variables
- Inserts chunk metadata into the chunks table
- Inserts vector embeddings into pgvector column
- Handles project and user associations
- Logs successes and failures
"""

import os
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from loguru import logger

class SupabaseWriter:
    def __init__(self, output_dir: str):
        """
        Initialize Supabase connection and prepare for writing.
        
        Args:
            output_dir: Directory for writing error logs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Ensure SUPABASE_URL and SUPABASE_KEY "
                "are set in your environment or .env file."
            )
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
    def write_chunks(self, 
                    chunks: List['TranscriptChunk'],
                    chunk_vectors: Dict[str, List[float]],
                    project_id: Optional[str] = None,
                    user_id: Optional[str] = None) -> bool:
        """
        Write transcript chunks and their vectors to Supabase.
        
        Args:
            chunks: List of TranscriptChunk objects
            chunk_vectors: Dict mapping chunk_id to vector embeddings
            project_id: Optional project identifier
            user_id: Optional user identifier
            
        Returns:
            bool: True if all writes succeeded, False if any failed
        """
        success = True
        
        for chunk in chunks:
            try:
                # Prepare chunk data
                chunk_data = {
                    "chunk_id": chunk.chunk_id,
                    "question_id": chunk.question_id,
                    "question_text": chunk.question_text,
                    "response_text": chunk.response_text,
                    "start_time": chunk.start_time,
                    "end_time": chunk.end_time,
                    "similarity_score": chunk.similarity_score,
                    "vector_embedding": chunk_vectors.get(chunk.chunk_id),
                }
                
                # Add optional fields if provided
                if project_id:
                    chunk_data["project_id"] = project_id
                if user_id:
                    chunk_data["user_id"] = user_id
                
                # Insert into Supabase
                result = self.supabase.table("chunks").insert(chunk_data).execute()
                
                # Log success
                logger.info(f"Successfully inserted chunk {chunk.chunk_id}")
                
            except Exception as e:
                error_msg = f"Failed to insert chunk {chunk.chunk_id}: {str(e)}"
                logger.error(error_msg)
                self._write_error(error_msg)
                success = False
                
        return success
    
    def _write_error(self, error_msg: str) -> None:
        """Write error message to log file."""
        error_path = self.output_dir / "errors.log"
        try:
            with open(error_path, "a", encoding="utf-8") as f:
                f.write(f"{error_msg}\n")
        except Exception as e:
            logger.error(f"Error writing to error log: {str(e)}")
