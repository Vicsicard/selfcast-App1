# Self Cast Studio App

A tool for processing interview videos into transcript chunks and video segments, with Supabase storage integration.

## Features

- ✅ Dual-mode support (VTT and Whisper)
- ✅ Video segmentation based on timestamps
- ✅ Transcript chunking and formatting
- ✅ Error handling and logging
- ✅ Video index generation
- ✅ Supabase storage integration
- ✅ File metadata tracking

## Storage Architecture

### Supabase Storage Buckets

- `videos/`: Stores video files (.mp4)
- `audio/`: Stores extracted audio files
- `documents/`: Stores transcripts and metadata files

### Database Tables

- `transcript_files`: Tracks all uploaded files with metadata
  - user_id: Links files to users
  - transcript_id: Groups related files
  - file_type: Tracks file types (video/mp4, text/plain, etc.)
  - file_name: Original file name
  - bucket: Storage bucket location

## Requirements

- Python 3.11+
- FFmpeg (install via `winget install Gyan.FFmpeg`)
- Python dependencies (install via `pip install -r requirements.txt`)
- Supabase project with storage enabled

See `DEPENDENCIES.md` for detailed dependency information for each mode.

## Environment Setup

Create a `.env` file with your Supabase credentials:
```bash
SUPABASE_URL=your-project-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## Verification Tools

- `verify_uploads.py`: Verifies file uploads and database consistency
  - Checks storage bucket access
  - Lists files in each bucket
  - Verifies database records
  - Reports file type statistics

## Usage

### VTT Mode
Use this mode when you have a pre-existing VTT transcript file:
```bash
python transcript_builder.py --vtt input.vtt --mp4 input.mp4 --category narrative_elevation
```

### Whisper Mode
Use this mode to generate transcripts from scratch using Whisper:
```bash
python transcript_builder.py --mp4 input.mp4 --category narrative_defense
```

### With Supabase Integration
```bash
python transcript_builder.py --mp4 input.mp4 --category narrative_defense --project-id your-project-id --user-id your-user-id
```

### Input Files

1. **Video File** (.mp4 format)
   - Your interview recording

2. **VTT File** (optional)
   - WebVTT format transcript with timestamps
   - Required for VTT mode

3. **Category** (required)
   - One of: narrative_defense, narrative_elevation, narrative_transition
   - Determines which question set to use

### Output Structure

The tool generates a job-specific output directory with:

```
output/
└── job_20250408_123456/
    ├── transcript_chunks.md     # Human-readable transcript
    ├── chunk_metadata.json      # Structured data about chunks
    └── video_chunks/           # Directory of video segments
        ├── chunk_001.mp4
        ├── chunk_002.mp4
        └── ...
```

#### Sample Output Files

1. **transcript_chunks.md**:
```markdown
# Interview Transcript

## Chunk 1 [00:00:15 - 00:01:30]
**Q:** Tell me about your background in technology.

I started programming when I was twelve...

---

## Chunk 2 [00:01:30 - 00:02:45]
**Q:** What inspired you to start this company?

The idea came to me when...
```

2. **chunk_metadata.json**:
```json
{
  "chunks": [
    {
      "start_time": 15.0,
      "end_time": 90.0,
      "text": "I started programming when I was twelve...",
      "speaker": "interviewee",
      "question": "Tell me about your background in technology",
      "question_id": "background_001",
      "similarity_score": 0.85,
      "video_path": "video_chunks/chunk_001.mp4"
    },
    ...
  ]
}
```

## Current Status

- ✅ Storage buckets configured and accessible
- ✅ Database schema implemented
- ✅ File upload functionality working
- ✅ Metadata tracking operational
- ✅ User access controls in place

Last verified: 2025-04-11
- 90 files in storage
- 89 database records
- 89 unique users
- File types: video/mp4 (83), video (2), text/plain (3), other (1)

## Future Improvements

### Planned Features
- [ ] VTT-only mode for non-video interviews
- [ ] Speaker diarization support
- [ ] Auto-title generation for chunks
- [ ] In-app chunk editing panel

### Technical Enhancements
- [ ] Parallel video processing
- [ ] Custom chunk merging rules
- [ ] Enhanced speaker detection
- [ ] Real-time progress updates

### UI/UX Improvements
- [ ] Web-based chunk editor
- [ ] Live transcription preview
- [ ] Batch processing support
- [ ] Custom output templates

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## Development Status

- [x] Core video segmentation
- [x] Error handling and logging
- [x] Video index generation
- [x] CLI interface
- [x] Cloud storage integration
- [ ] GUI interface (planned)
- [ ] Batch processing (planned)

## License

MIT License - See LICENSE file for details
