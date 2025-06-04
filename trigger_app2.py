#!/usr/bin/env python
"""
App 2 Trigger - Sends processed transcript chunks to App 2 for style profiling
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
import uuid
from loguru import logger

# Check Python version - critical requirement is Python 3.10
if not sys.version.startswith("3.10"):
    print(f"⛔ ERROR: This script requires Python 3.10. You are using {sys.version.split()[0]}")
    print("Please activate the venv310 environment and try again.")
    sys.exit(1)

# Import MongoDB client
from utils.mongodb_client import get_mongodb_client

# Set up logging
logger.add("logs/app2_trigger.log", rotation="1 day", level="INFO")

# App 2 webhook URL (to be configured in environment)
APP2_WEBHOOK_URL = os.environ.get('APP2_WEBHOOK_URL', 'http://localhost:5001/api/webhook/transcript')

def trigger_app2_processing(transcript_id, chunks_id):
    """Trigger App 2 processing via webhook.
    
    Args:
        transcript_id: MongoDB ID of transcript
        chunks_id: MongoDB ID of chunks document
        
    Returns:
        dict: Response from App 2 webhook
    """
    try:
        logger.info(f"Triggering App 2 processing for transcript {transcript_id}")
        
        # Get MongoDB client
        mongodb = get_mongodb_client()
        
        # Get transcript data
        transcript = mongodb.get_transcript(transcript_id)
        if not transcript:
            logger.error(f"Transcript {transcript_id} not found")
            return {
                "success": False,
                "error": "Transcript not found"
            }
        
        # Get chunks data
        chunks = mongodb.get_transcript_chunks(chunks_id)
        if not chunks:
            logger.error(f"Chunks {chunks_id} not found")
            return {
                "success": False,
                "error": "Chunks not found"
            }
        
        # Prepare webhook payload
        payload = {
            "transcript_id": transcript_id,
            "chunks_id": chunks_id,
            "user_id": transcript.get('user_id'),
            "email": transcript.get('email'),
            "category": transcript.get('category')
        }
        
        # Send webhook request
        logger.info(f"Sending webhook request to {APP2_WEBHOOK_URL}")
        response = requests.post(
            APP2_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # Check response
        if response.status_code == 200:
            logger.info(f"App 2 processing triggered successfully: {response.json()}")
            return {
                "success": True,
                "response": response.json()
            }
        else:
            logger.error(f"Failed to trigger App 2 processing: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        logger.error(f"Error triggering App 2 processing: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def create_processing_task(transcript_id, chunks_id):
    """Create a processing task in MongoDB for App 2.
    
    This allows App 2 to poll for new tasks if webhooks are not available.
    
    Args:
        transcript_id: MongoDB ID of transcript
        chunks_id: MongoDB ID of chunks document
        
    Returns:
        str: Task ID
    """
    try:
        logger.info(f"Creating processing task for transcript {transcript_id}")
        
        # Get MongoDB client
        mongodb = get_mongodb_client()
        
        # Create task
        task = {
            'transcript_id': transcript_id,
            'chunks_id': chunks_id,
            'type': 'style_profile',
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Save to processing_tasks collection
        result = mongodb.db.processing_tasks.insert_one(task)
        task_id = str(result.inserted_id)
        
        logger.info(f"Created processing task with ID: {task_id}")
        
        return task_id
    except Exception as e:
        logger.error(f"Error creating processing task: {str(e)}")
        return None

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trigger App 2 processing")
    parser.add_argument("--transcript-id", required=True, help="MongoDB ID of transcript")
    parser.add_argument("--chunks-id", required=True, help="MongoDB ID of chunks document")
    parser.add_argument("--webhook", action="store_true", help="Use webhook instead of task")
    args = parser.parse_args()
    
    transcript_id = args.transcript_id
    chunks_id = args.chunks_id
    
    if args.webhook:
        # Trigger via webhook
        result = trigger_app2_processing(transcript_id, chunks_id)
        
        if result.get("success"):
            print("\n✅ App 2 processing triggered successfully!")
        else:
            print(f"\n❌ Failed to trigger App 2 processing: {result.get('error')}")
            
            # Create task as fallback
            print("\n🔄 Creating processing task as fallback...")
            task_id = create_processing_task(transcript_id, chunks_id)
            
            if task_id:
                print(f"\n✅ Created processing task with ID: {task_id}")
            else:
                print("\n❌ Failed to create processing task")
    else:
        # Create processing task
        task_id = create_processing_task(transcript_id, chunks_id)
        
        if task_id:
            print(f"\n✅ Created processing task with ID: {task_id}")
        else:
            print("\n❌ Failed to create processing task")

if __name__ == "__main__":
    main()
