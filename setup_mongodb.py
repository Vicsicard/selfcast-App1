#!/usr/bin/env python
"""
MongoDB Setup - Creates required collections and indexes
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from pymongo import MongoClient, ASCENDING, TEXT

# Check Python version - critical requirement is Python 3.10
if not sys.version.startswith("3.10"):
    print(f"⛔ ERROR: This script requires Python 3.10. You are using {sys.version.split()[0]}")
    print("Please activate the venv310 environment and try again.")
    sys.exit(1)

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"mongodb_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure logging
logger.add(log_file, rotation="1 day", level="INFO")

# MongoDB connection details
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv://vicsicard:Z6T46srM9kEGZfLJ@cluster0.tfi0dul.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
MONGODB_DB = os.environ.get('MONGODB_DB', 'new-self-website-5-15-25')

def connect_mongodb():
    """Connect to MongoDB and return the database connection."""
    try:
        logger.info(f"Connecting to MongoDB: {MONGODB_URI}")
        client = MongoClient(MONGODB_URI)
        
        # Verify connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Get database
        db = client[MONGODB_DB]
        logger.info(f"Using database: {MONGODB_DB}")
        
        return db, client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        print(f"\n❌ Error connecting to MongoDB: {str(e)}")
        return None, None

def setup_collections(db):
    """Set up MongoDB collections and indexes."""
    try:
        # Create collections if they don't exist
        collections = [
            'transcripts',
            'transcript_chunks',
            'transcript_files',
            'processing_tasks'
        ]
        
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
            else:
                logger.info(f"Collection already exists: {collection_name}")
        
        # Set up indexes for transcripts collection
        transcripts = db.transcripts
        transcripts.create_index([("user_id", ASCENDING)], background=True)
        transcripts.create_index([("email", ASCENDING)], background=True)
        transcripts.create_index([("status", ASCENDING)], background=True)
        transcripts.create_index([("created_at", ASCENDING)], background=True)
        logger.info("Created indexes for transcripts collection")
        
        # Set up indexes for transcript_chunks collection
        chunks = db.transcript_chunks
        chunks.create_index([("transcript_id", ASCENDING)], background=True)
        chunks.create_index([("chunks.text", TEXT)], background=True)
        logger.info("Created indexes for transcript_chunks collection")
        
        # Set up indexes for transcript_files collection
        files = db.transcript_files
        files.create_index([("transcript_id", ASCENDING)], background=True)
        files.create_index([("user_id", ASCENDING)], background=True)
        files.create_index([("file_type", ASCENDING)], background=True)
        logger.info("Created indexes for transcript_files collection")
        
        # Set up indexes for processing_tasks collection
        tasks = db.processing_tasks
        tasks.create_index([("status", ASCENDING)], background=True)
        tasks.create_index([("transcript_id", ASCENDING)], background=True)
        tasks.create_index([("created_at", ASCENDING)], background=True)
        logger.info("Created indexes for processing_tasks collection")
        
        return True
    except Exception as e:
        logger.error(f"Failed to set up collections: {str(e)}")
        print(f"\n❌ Error setting up collections: {str(e)}")
        return False

def main():
    """Main entry point."""
    print("\n🔄 Setting up MongoDB collections and indexes...")
    
    # Connect to MongoDB
    db, client = connect_mongodb()
    if db is None:
        print("\n❌ Failed to connect to MongoDB. Exiting.")
        sys.exit(1)
    
    # Set up collections and indexes
    if setup_collections(db):
        print("\n✅ MongoDB setup completed successfully!")
    else:
        print("\n❌ MongoDB setup failed.")
    
    # Close connection
    if client:
        client.close()
        logger.info("MongoDB connection closed")

if __name__ == "__main__":
    main()
