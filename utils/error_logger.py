import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import traceback
from supabase import create_client, Client

def setup_error_logger(app_name: str) -> logging.Logger:
    """Set up a logger for the specified app that writes to both file and console."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.ERROR)
    
    # File handler - writes to windsurf_errors.log
    file_handler = logging.FileHandler(log_dir / "windsurf_errors.log")
    file_handler.setLevel(logging.ERROR)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_error_to_workflow(
    error: Exception,
    app_name: str,
    job_id: Optional[str] = None,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None
) -> None:
    """Log error to Supabase workflow_logs table."""
    try:
        if not (supabase_url and supabase_key):
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            
        if not (supabase_url and supabase_key):
            raise ValueError("Supabase credentials not found")
            
        supabase: Client = create_client(supabase_url, supabase_key)
        
        error_data = {
            "app_name": app_name,
            "status": "error",
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "stacktrace": traceback.format_exc()
        }
        
        if job_id:
            error_data["job_id"] = job_id
            
        supabase.table("workflow_logs").insert(error_data).execute()
        
    except Exception as e:
        # If we can't log to Supabase, at least log to file
        logger = setup_error_logger("workflow_logger")
        logger.error(f"Failed to log error to workflow_logs: {str(e)}")

def handle_app_error(
    error: Exception,
    app_name: str = "Transcript Builder",
    job_id: Optional[str] = None,
    log_to_workflow: bool = True
) -> None:
    """Central error handling function for all apps."""
    # Set up logger
    logger = setup_error_logger(app_name)
    
    # Log the full error with traceback
    error_msg = (
        f"Error in {app_name}\n"
        f"Error Type: {type(error).__name__}\n"
        f"Error Message: {str(error)}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )
    logger.error(error_msg)
    
    # Optionally log to workflow_logs table
    if log_to_workflow:
        log_error_to_workflow(error, app_name, job_id)
