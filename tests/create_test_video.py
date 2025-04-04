"""
Create a test video for video segmentation testing.
"""
import ffmpeg
from pathlib import Path

def create_test_video():
    """Create a 60-second test video with a color pattern."""
    TEST_DIR = Path(__file__).parent
    TEMP_DIR = TEST_DIR / 'temp'
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    output_path = TEMP_DIR / 'input.mp4'
    
    # Create a test pattern video
    stream = ffmpeg.input('testsrc=duration=60:size=320x240:rate=30', f='lavfi')
    stream = ffmpeg.output(stream, str(output_path), acodec='none')
    ffmpeg.run(stream, overwrite_output=True)
    
    return output_path

if __name__ == '__main__':
    video_path = create_test_video()
    print(f"Created test video: {video_path}")
