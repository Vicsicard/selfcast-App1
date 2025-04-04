# Self Cast Studio App

A tool for processing interview videos into transcript chunks and video segments, with Supabase storage integration.

## Features

- ✅ Video segmentation based on timestamps
- ✅ Transcript chunking and formatting
- ✅ Error handling and logging
- ✅ Video index generation
- ✅ Supabase storage integration
- ✅ File metadata tracking

## Requirements

- Python 3.11+
- FFmpeg (install via `winget install Gyan.FFmpeg`)
- Python dependencies (install via `pip install -r requirements.txt`)
- Supabase project with storage enabled

## Environment Setup

Create a `.env` file with your Supabase credentials:
```bash
SUPABASE_URL=your-project-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## Usage

### Basic Command
```bash
python transcript_builder.py --mp4 interview.mp4 --category narrative_defense
```

### With Supabase Integration
```bash
python transcript_builder.py --mp4 interview.mp4 --category narrative_defense --project-id your-project-id --user-id your-user-id
```

### Input Files

1. **Video File** (.mp4 format)
   - Your interview recording

2. **Category** (required)
   - One of: narrative_defense, narrative_elevation, narrative_transition
   - Determines which question set to use

### Output Structure

```
output/
├── chunks/              # Segmented video files
│   ├── Q01_chunk_1.mp4
│   ├── Q02_chunk_2.mp4
│   └── ...
├── transcript.md        # Formatted transcript
├── metadata.json       # Chunk metadata
├── video_index.json    # Chunk to video mappings
└── errors.log         # Processing errors
```

### Supabase Storage Structure

```
videos/
├── {user_id}/
│   └── {transcript_id}/
│       ├── original.mp4
│       ├── Q01_chunk_1.mp4
│       └── ...
documents/
├── {user_id}/
│   └── {transcript_id}/
│       ├── transcript.md
│       ├── metadata.json
│       └── video_index.json
```

## Features

### Video Segmentation
- Automatically creates video segments from timestamps
- Preserves original video quality using stream copy
- Skips existing segments to prevent overwrites
- Generates standardized filenames (Q[question_id]_chunk_[number].mp4)

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

### Supabase Integration
- Automatic file uploads to Supabase Storage
- Organized storage structure by user and transcript
- File metadata tracking in database
- Row-level security for user data protection
- Separate buckets for videos and documents

## Development Status

- [x] Core video segmentation
- [x] Error handling and logging
- [x] Video index generation
- [x] CLI interface
- [x] Cloud storage integration
- [ ] GUI interface (planned)
- [ ] Batch processing (planned)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details
