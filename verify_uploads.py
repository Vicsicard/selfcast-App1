"""Verify that files were uploaded correctly to Supabase Storage."""
import os
from typing import Dict, List
from utils.supabase_client import get_client

def verify_storage_access() -> None:
    """Verify access to storage buckets and list contents."""
    supabase = get_client()
    buckets = ["videos", "audio", "documents"]
    
    print("\nVerifying storage access...")
    for bucket in buckets:
        try:
            # List files in bucket
            result = supabase.storage.from_(bucket).list()
            print(f"\n[OK] Can access {bucket}/ bucket")
            
            # Show some example files
            if result:
                print(f"Found {len(result)} files:")
                try:
                    for item in result[:5]:  # Show first 5 files
                        name = str(item['name']) if isinstance(item, dict) else str(item)
                        print(f"  - {name}")
                    if len(result) > 5:
                        print(f"  - ... and {len(result)-5} more")
                except Exception as e:
                    print(f"[WARNING] Could not parse file details: {str(e)}")
                    print(f"Raw result: {result[:5]}")
            else:
                print("  No files found")
                
        except Exception as e:
            print(f"[ERROR] Cannot access {bucket}/ bucket: {str(e)}")

def verify_database_access() -> None:
    """Verify access to transcript_files table."""
    supabase = get_client()
    print("\nVerifying database access...")
    try:
        result = supabase.table("transcript_files").select("*").execute()
        entries = result.data
        
        if entries:
            print(f"[OK] Found {len(entries)} entries in transcript_files table")
            
            # Group by user_id
            users: Dict[str, Dict[str, List[str]]] = {}
            for entry in entries:
                uid = entry.get('user_id', 'unknown')
                if uid not in users:
                    users[uid] = {'files': []}
                users[uid]['files'].append(entry.get('file_name', 'unknown'))
            
            print(f"[OK] Found {len(users)} unique users")
            for uid, data in list(users.items())[:5]:  # Show first 5 users
                print(f"  - User {uid}: {len(data['files'])} files")
            if len(users) > 5:
                print(f"  - ... and {len(users)-5} more users")
                
            # Group by file type
            file_types: Dict[str, List[str]] = {}
            for entry in entries:
                ftype = entry.get('file_type', 'unknown')
                if ftype not in file_types:
                    file_types[ftype] = []
                file_types[ftype].append(entry.get('file_name', 'unknown'))
            
            print("\nFile types:")
            for ftype, files in file_types.items():
                print(f"  - {ftype or 'unknown'}: {len(files)} files")
                
        else:
            print("[WARNING] No entries found in transcript_files table")
            
    except Exception as e:
        print(f"[ERROR] Cannot access transcript_files table: {str(e)}")

if __name__ == "__main__":
    print("Running Supabase storage verification...")
    verify_storage_access()
    verify_database_access()
