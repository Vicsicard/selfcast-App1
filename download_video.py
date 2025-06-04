"""
Download video file from Supabase storage.
"""
import os
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")  # Using SUPABASE_KEY for anon key
    
    if not url or not key:
        raise EnvironmentError("Missing Supabase credentials")
    
    # Initialize Supabase client
    supabase = create_client(url, key)
    print("[*] Connected to Supabase")
    
    # Create input directory if it doesn't exist
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)
    
    # Download test_sample_30s.mp4 from the most recent directory
    # Using the latest directory from SQL results
    content_path = "test_ws_upload/test_video.mp4"  # This is a known working path from SQL results
    output_path = input_dir / "test_video.mp4"  # Save without the directory structure
    
    print(f"[*] Downloading {content_path} from videos bucket...")
    try:
        # Download the file directly
        with open(output_path, 'wb+') as f:
            data = supabase.storage.from_('videos').download(content_path)
            f.write(data)
        print(f"[+] Successfully downloaded to {output_path}")
            
    except Exception as e:
        print(f"[-] Error downloading {content_path}: {str(e)}")
        if hasattr(e, 'message'):
            print(f"[-] Error message: {e.message}")
        raise

if __name__ == "__main__":
    main()
