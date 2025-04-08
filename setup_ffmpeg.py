import os
import zipfile
import urllib.request
import shutil
from pathlib import Path

def download_ffmpeg():
    # Using the zip version instead of 7z
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    download_path = "ffmpeg.zip"
    
    print("Downloading FFmpeg...")
    try:
        urllib.request.urlretrieve(url, download_path)
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return
    
    print("Extracting FFmpeg...")
    try:
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall()
    except Exception as e:
        print(f"Error extracting FFmpeg: {e}")
        os.remove(download_path)
        return
    
    # Find the bin directory
    try:
        ffmpeg_dir = next(Path().glob("ffmpeg-*"))
    except StopIteration:
        print("Error finding FFmpeg directory")
        os.remove(download_path)
        return
    
    bin_dir = ffmpeg_dir / "bin"
    
    # Copy FFmpeg files to system32
    print("Installing FFmpeg...")
    required_files = ['ffmpeg.exe', 'ffplay.exe', 'ffprobe.exe']
    for filename in required_files:
        src = bin_dir / filename
        dest = Path(r"C:\Windows\System32") / filename
        try:
            if src.exists():
                shutil.copy2(src, dest)
                print(f"Copied {filename}")
            else:
                print(f"Warning: {filename} not found")
        except Exception as e:
            print(f"Error copying {filename}: {e}")
    
    # Cleanup
    try:
        os.remove(download_path)
        shutil.rmtree(ffmpeg_dir)
    except Exception as e:
        print(f"Error cleaning up: {e}")
    
    print("FFmpeg installation complete! Press Enter to exit...")

if __name__ == "__main__":
    download_ffmpeg()
