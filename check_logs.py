from pathlib import Path
import json
from datetime import datetime, timedelta
import os

def check_logs():
    """Check both file logs and Supabase workflow logs for recent errors."""
    print("\n=== Checking logs at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "===")
    
    # Check file logs
    log_file = Path("logs/windsurf_errors.log")
    if log_file.exists():
        with open(log_file) as f:
            lines = f.readlines()
            # Get last 10 lines or all if less than 10
            recent_logs = lines[-10:]
            if recent_logs:
                print("\nRecent file log entries:")
                for line in recent_logs:
                    print(line.strip())
            else:
                print("\nNo recent file log entries found")
    else:
        print("\nNo error log file found - this means no errors have occurred yet")
    
    # Check output directory size and files
    output_dir = Path("output")
    if output_dir.exists():
        print("\nOutput directory status:")
        total_size = 0
        for file in output_dir.glob("*"):
            size = file.stat().st_size
            modified = datetime.fromtimestamp(file.stat().st_mtime)
            total_size += size
            print(f"- {file.name}: {size/1024/1024:.2f} MB (Modified: {modified.strftime('%H:%M:%S')})")
        print(f"Total output size: {total_size/1024/1024:.2f} MB")
    else:
        print("\nNo output directory found yet")

if __name__ == "__main__":
    check_logs()
