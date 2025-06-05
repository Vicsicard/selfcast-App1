#!/usr/bin/env python
"""
MongoDB Client - Handles MongoDB connections and operations
Replaces Supabase storage with MongoDB for transcript processing
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from pymongo import MongoClient
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

# MongoDB connection details
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv://vicsicard:Z6T46srM9kEGZfLJ@cluster0.tfi0dul.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
MONGODB_DB = os.environ.get('MONGODB_DB', 'new-self-website-5-15-25')

class MongoDBClient:
    """MongoDB client for transcript processing."""
    
    def __init__(self):
        """Initialize MongoDB client."""
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB."""
        try:
            logger.info(f"Connecting to MongoDB: {MONGODB_URI}")
            self.client = MongoClient(MONGODB_URI)
            
            # Verify connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Get database
            self.db = self.client[MONGODB_DB]
            logger.info(f"Using database: {MONGODB_DB}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def save_transcript(self, transcript_data):
        """Save transcript data to MongoDB.
        
        Args:
            transcript_data: Dictionary with transcript data
            
        Returns:
            str: MongoDB ID of saved transcript
        """
        try:
            # Add timestamps
            if 'created_at' not in transcript_data:
                from datetime import datetime
                transcript_data['created_at'] = datetime.now().isoformat()
                transcript_data['updated_at'] = transcript_data['created_at']
            
            # Save to transcripts collection
            result = self.db.transcripts.insert_one(transcript_data)
            transcript_id = str(result.inserted_id)
            logger.info(f"Saved transcript to MongoDB with ID: {transcript_id}")
            
            return transcript_id
        except Exception as e:
            logger.error(f"Failed to save transcript to MongoDB: {str(e)}")
            return None
    
    def update_transcript(self, transcript_id, update_data):
        """Update transcript data in MongoDB.
        
        Args:
            transcript_id: MongoDB ID of transcript
            update_data: Dictionary with fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add updated timestamp
            from datetime import datetime
            update_data['updated_at'] = datetime.now().isoformat()
            
            # Update transcript
            result = self.db.transcripts.update_one(
                {'_id': ObjectId(transcript_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated transcript {transcript_id} in MongoDB")
                return True
            else:
                logger.warning(f"No changes made to transcript {transcript_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to update transcript in MongoDB: {str(e)}")
            return False
    
    def get_transcript(self, transcript_id):
        """Get transcript data from MongoDB.
        
        Args:
            transcript_id: MongoDB ID of transcript
            
        Returns:
            dict: Transcript data or None if not found
        """
        try:
            transcript = self.db.transcripts.find_one({'_id': ObjectId(transcript_id)})
            if transcript:
                # Convert ObjectId to string for JSON serialization
                transcript['_id'] = str(transcript['_id'])
                return transcript
            else:
                logger.warning(f"Transcript {transcript_id} not found in MongoDB")
                return None
        except Exception as e:
            logger.error(f"Failed to get transcript from MongoDB: {str(e)}")
            return None
    
    def save_transcript_chunks(self, transcript_id, chunks, metadata=None):
        """Save transcript chunks to MongoDB.
        
        Args:
            transcript_id: MongoDB ID of transcript
            chunks: List of transcript chunks
            metadata: Optional metadata about the chunks
            
        Returns:
            str: MongoDB ID of saved chunks document
        """
        try:
            # Create chunks document
            chunks_data = {
                'transcript_id': transcript_id,
                'chunks': chunks,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to transcript_chunks collection
            result = self.db.transcript_chunks.insert_one(chunks_data)
            chunks_id = str(result.inserted_id)
            logger.info(f"Saved transcript chunks to MongoDB with ID: {chunks_id}")
            
            # Update transcript with chunks_id
            self.update_transcript(transcript_id, {
                'chunks_id': chunks_id,
                'status': 'processed'
            })
            
            return chunks_id
        except Exception as e:
            logger.error(f"Failed to save transcript chunks to MongoDB: {str(e)}")
            return None
    
    def get_transcript_chunks(self, chunks_id):
        """Get transcript chunks from MongoDB.
        
        Args:
            chunks_id: MongoDB ID of chunks document
            
        Returns:
            dict: Chunks data or None if not found
        """
        try:
            chunks = self.db.transcript_chunks.find_one({'_id': ObjectId(chunks_id)})
            if chunks:
                # Convert ObjectId to string for JSON serialization
                chunks['_id'] = str(chunks['_id'])
                return chunks
            else:
                logger.warning(f"Transcript chunks {chunks_id} not found in MongoDB")
                return None
        except Exception as e:
            logger.error(f"Failed to get transcript chunks from MongoDB: {str(e)}")
            return None
    
    def trigger_app2_processing(self, transcript_id, chunks_id):
        """Trigger App 2 processing by creating a processing task.
        
        Args:
            transcript_id: MongoDB ID of transcript
            chunks_id: MongoDB ID of chunks document
            
        Returns:
            str: MongoDB ID of processing task
        """
        try:
            # Get transcript data to include in task
            transcript = self.get_transcript(transcript_id)
            
            if not transcript:
                logger.error(f"Cannot trigger App 2 processing: Transcript {transcript_id} not found")
                return None
            
            # Create processing task
            task_data = {
                'transcript_id': transcript_id,
                'chunks_id': chunks_id,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'app': 'app2',
                'metadata': {
                    'email': transcript.get('email'),
                    'category': transcript.get('category'),
                    'project_code': transcript.get('project_code')  # Include the 4-digit project code
                }
            }
            
            # Save to processing_tasks collection
            result = self.db.processing_tasks.insert_one(task_data)
            task_id = str(result.inserted_id)
            logger.info(f"Created App 2 processing task with ID: {task_id}")
            
            return task_id
        except Exception as e:
            logger.error(f"Failed to trigger App 2 processing: {str(e)}")
            return None

# Initialize MongoDB client
mongodb_client = MongoDBClient()

def get_mongodb_client():
    """Get MongoDB client instance."""
    if not mongodb_client.client:
        mongodb_client.connect()
    return mongodb_client
