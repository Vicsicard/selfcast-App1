# Self Cast Studio App

A tool for processing interview videos into transcript chunks and video segments.

## Features

- ✅ Video segmentation based on timestamps
- ✅ Transcript chunking and formatting
- ✅ Error handling and logging
- ✅ Video index generation

## Requirements

- Python 3.11+
- FFmpeg (install via `winget install Gyan.FFmpeg`)
- Python dependencies (install via `pip install -r requirements.txt`)

## Usage

### Basic Command
```bash
python process_interview.py interview.mp4 chunk_metadata.json
```

### Advanced Options
```bash
python process_interview.py interview.mp4 chunk_metadata.json --output-dir output --error-log errors.log
```

### Input Files

1. **Video File** (.mp4 format)
   - Your interview recording

2. **Chunk Metadata** (chunk_metadata.json)
```json
{
  "chunks": [
    {
      "chunk_id": "intro_001",
      "question_id": "01",
      "start_time": "00:00:00",
      "end_time": "00:00:15"
    }
  ]
}
```

### Output Structure

```
output/
├── video_chunks/         # Segmented video files
│   ├── Q01_intro_001.mp4
│   ├── Q02_pivot_002.mp4
│   └── ...
├── video_index.json     # Chunk to video mappings
└── errors.log          # Processing errors
```

## Features

### Video Segmentation
- Automatically creates video segments from timestamps
- Preserves original video quality using stream copy
- Skips existing segments to prevent overwrites
- Generates standardized filenames (Q[question_id]_[chunk_id].mp4)

### Error Handling
- Continues processing if individual segments fail
- Logs errors with timestamps and details
- Excludes failed segments from video index
- Creates clean error reports

### Video Index
- JSON-based index of all successful segments
- Maps chunk IDs to video files
- Includes timestamps and question IDs
- Helps track processed content

## Development Status

- [x] Core video segmentation
- [x] Error handling and logging
- [x] Video index generation
- [x] CLI interface
- [ ] GUI interface (planned)
- [ ] Batch processing (planned)
- [ ] Cloud storage integration (planned)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details
