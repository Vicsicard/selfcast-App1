#!/usr/bin/env python
"""
MongoDB Webhook Handler - Receives transcripts from Unified system
Processes transcripts and triggers App 2 using MongoDB
"""

import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
import uuid
from flask import Flask, request, jsonify
from loguru import logger
import sys

# Set up logging
os.makedirs("logs", exist_ok=True)
logger.add("logs/webhook_mongodb.log", rotation="1 day", level="INFO")

# Import MongoDB client
from utils.mongodb_client import get_mongodb_client

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB client
mongodb = get_mongodb_client()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Ping MongoDB to check connection
        mongodb.client.admin.command('ping')
        
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "mongodb_status": "connected"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 500

@app.route('/api/webhook/transcript', methods=['POST'])
def receive_transcript():
    """Receive transcript from Unified system."""
    try:
        # Get request data
        data = request.json
        if not data:
            logger.error("No data received")
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        logger.info(f"Received transcript data: {json.dumps(data)[:100]}...")
        
        # Extract required fields
        transcript_id = data.get("transcript_id")
        vtt_content = data.get("vtt_content")
        user_id = data.get("user_id")
        category = data.get("category", "general")
        email = data.get("email")
        project_code = data.get("project_code")  # Extract the 4-digit project code
        
        logger.info(f"Received transcript with project code: {project_code}")
        
        # Validate required fields
        if not transcript_id or not vtt_content:
            logger.error("Missing required fields")
            return jsonify({
                "status": "error", 
                "message": "Missing required fields: transcript_id and vtt_content are required"
            }), 400
        
        # Create temporary VTT file
        with tempfile.NamedTemporaryFile(suffix=".vtt", delete=False, mode="w", encoding="utf-8") as temp_vtt:
            temp_vtt.write(vtt_content)
            temp_vtt_path = temp_vtt.name
            logger.info(f"Created temporary VTT file: {temp_vtt_path}")
        
        # Create temporary output directory
        temp_output_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary output directory: {temp_output_dir}")
        
        try:
            # Process VTT file using our simplified processor
            from webhook_transcript_processor import process_vtt
            processed_chunks = process_vtt(
                vtt_path=temp_vtt_path,
                email=email
            )
            
            if not processed_chunks:
                logger.error("Failed to process VTT file")
                return jsonify({"status": "error", "message": "Failed to process VTT file"}), 500
            
            # Save transcript data to MongoDB
            transcript_data = {
                "transcript_id": transcript_id,
                "user_id": user_id,
                "category": category,
                "email": email,
                "project_code": project_code,  # Store the 4-digit project code
                "created_at": datetime.now().isoformat(),
                "status": "processed"
            }
            
            # Save transcript to MongoDB
            saved_id = mongodb.save_transcript(transcript_data)
            logger.info(f"Saved transcript to MongoDB with ID: {saved_id}")
            
            # Save transcript chunks to MongoDB
            chunks_id = mongodb.save_transcript_chunks(saved_id, processed_chunks)
            logger.info(f"Saved {len(processed_chunks)} chunks to MongoDB with ID: {chunks_id}")
            
            # Trigger App 2 processing
            task_id = mongodb.trigger_app2_processing(saved_id, chunks_id)
            logger.info(f"Triggered App 2 processing with task ID: {task_id}")
            
            # Return success response
            return jsonify({
                "status": "success",
                "message": "Transcript processed successfully",
                "transcript_id": str(saved_id),
                "chunks_id": str(chunks_id),
                "task_id": str(task_id),
                "chunks_count": len(processed_chunks)
            }), 200
            
        except Exception as e:
            logger.error(f"Error processing transcript: {str(e)}")
            return jsonify({"status": "error", "message": f"Error processing transcript: {str(e)}"}), 500
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_vtt_path)
                logger.info(f"Removed temporary VTT file: {temp_vtt_path}")
            except Exception as e:
                logger.error(f"Error removing temporary VTT file: {str(e)}")
            
            try:
                import shutil
                shutil.rmtree(temp_output_dir)
                logger.info(f"Removed temporary output directory: {temp_output_dir}")
            except Exception as e:
                logger.error(f"Error removing temporary output directory: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error handling webhook request: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error handling webhook request: {str(e)}",
            "details": str(e)
        }), 500

def run_server(host='0.0.0.0', port=5000):
    """Run the Flask server."""
    from werkzeug.serving import run_simple
    
    # Log startup
    logger.info(f"Starting MongoDB webhook handler on port {port}")
    print(f"\n🚀 Starting MongoDB webhook handler on port {port}")
    print(f"💻 Server URL: http://localhost:{port}")
    print(f"🔍 Health check: http://localhost:{port}/health")
    print(f"📝 Webhook endpoint: http://localhost:{port}/api/webhook/transcript")
    print("\n🟡 Press CTRL+C to stop the server\n")
    
    try:
        # Run Flask app with Werkzeug server
        run_simple(host, port, app, use_reloader=False, use_debugger=False)
    except KeyboardInterrupt:
        print("\n🚫 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")
        logger.error(f"Error starting server: {str(e)}")
    finally:
        print("\n💪 MongoDB webhook handler shutdown complete")

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    run_server(port=port)
