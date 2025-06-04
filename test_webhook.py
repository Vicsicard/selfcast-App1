#!/usr/bin/env python
"""
Test Webhook - Sends a test request to the webhook handler
"""

import requests
import json
import sys
import os
from pathlib import Path

def send_test_request():
    """Send a test request to the webhook handler."""
    
    # Webhook URL
    webhook_url = "http://localhost:5000/api/webhook/transcript"
    
    # Create test VTT content
    vtt_content = """WEBVTT

00:00:00.000 --> 00:00:05.000
Speaker 1: Hello, this is a test transcript.

00:00:05.000 --> 00:00:10.000
Speaker 2: This is a test response.

00:00:10.000 --> 00:00:15.000
Speaker 1: Thank you for testing the webhook handler.
"""
    
    # Create test payload
    payload = {
        "transcript_id": "test_transcript_123",
        "vtt_content": vtt_content,
        "user_id": "test_user",
        "category": "test",
        "email": "test@example.com"
    }
    
    print("\n🚀 Sending test request to webhook handler...")
    
    try:
        # First check if the server is running
        health_response = requests.get("http://localhost:5000/health")
        if health_response.status_code != 200:
            print(f"\n❌ Webhook handler is not running. Health check failed with status code: {health_response.status_code}")
            return False
        
        print(f"\n✅ Webhook handler is running. Health check response: {health_response.json()}")
        
        # Send webhook request
        response = requests.post(webhook_url, json=payload)
        
        # Check response
        if response.status_code == 200:
            print(f"\n✅ Test request successful!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"\n❌ Test request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Failed to connect to webhook handler. Is it running on port 5000?")
        return False
    except Exception as e:
        print(f"\n❌ Error sending test request: {str(e)}")
        return False

if __name__ == "__main__":
    send_test_request()
