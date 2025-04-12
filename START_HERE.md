# Transcript Builder Setup Guide

## 🚨 CRITICAL: Python Version Requirement
This application MUST run on Python 3.10 ONLY. No other versions are supported.

## 1. Initial Setup

### 1.1 Python Environment
1. Verify Python 3.10:
   ```bash
   python --version  # Must show Python 3.10.x
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv310
   .\venv310\Scripts\activate
   ```

### 1.2 Environment Variables
1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Update `.env` with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

### 1.3 Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Directory Structure
Ensure these directories exist and are properly set up:
```
/
├── docs/                    # Documentation
│   ├── OPERATIONS.md       # Master workflow
│   └── TROUBLESHOOTING.md  # Common issues and solutions
├── input/                  # Source files go here
├── output/                 # Processing output
├── completed_transcripts/  # Final MD files (YYYYMMDD_HHMMSS_category)
├── utils/                  # Processing utilities
└── tests/                 # Test files
```

## 3. Supabase Storage Structure
The application uses three Supabase storage buckets:
- `documents/` - For transcripts (.md) and metadata (.json)
- `videos/` - For video files (.mp4)
- `audio/` - For temporary audio processing (not stored)

## 4. Running the Application

### 4.1 VTT Mode
Process a VTT file:
```bash
python transcript_builder.py --vtt input/your_file.vtt --category your_category
```

### 4.2 MP4 Mode
Process an MP4 file:
```bash
python transcript_builder.py --mp4 input/your_file.mp4 --category your_category
```

### 4.3 M4A Mode (Audio Only)
Process an M4A audio file:
```bash
python transcript_builder.py --m4a input/your_file.m4a --category your_category
```

### 4.4 Output Directory
You can specify a custom output directory:
```bash
python transcript_builder.py --m4a input/your_file.m4a --category your_category --output custom_output
```

## 5. Verifying Outputs

### 5.1 Check Storage Access
Test Supabase connection and storage access:
```bash
python -m utils.verify_outputs --job_id your_job_id [--has_video] [--has_audio]
```

Example:
```bash
python -m utils.verify_outputs --job_id job_20250412_093712 --has_audio
```

### 5.2 Expected Files
The following files should be present after processing:
1. In `documents/` bucket:
   - `chunk_metadata.json`
   - `transcript_chunks.md`
   - `video_index.json`
2. In `videos/` bucket (if processing video):
   - Video chunks (.mp4)
3. Audio files:
   - Processed locally only, not stored in Supabase
   - Temporary WAV files are created for Whisper processing

## 6. Troubleshooting

### 6.1 Common Issues
1. **Python Version**: Must be exactly 3.10.x
2. **Environment**: Always use venv310
3. **Storage Access**: Run verify_outputs.py to check storage access
4. **Missing Files**: Check both local and Supabase storage
5. **Module Import**: Always run verify_outputs as a module:
   ```bash
   python -m utils.verify_outputs
   ```

### 6.2 Verification Failed
If verification fails:
1. Check `.env` has correct credentials
2. Verify all required files exist locally
3. Check Supabase storage access
4. Review logs for specific error messages
5. Note: Audio files are not stored in Supabase

## 7. Quality Control Checklist
- [ ] Python 3.10 is active
- [ ] Virtual environment is activated
- [ ] Environment variables are set
- [ ] Input files are in correct location
- [ ] Storage verification passes
- [ ] Output files are in completed_transcripts
- [ ] Required files are uploaded to Supabase:
  - [ ] Transcript and metadata files in documents bucket
  - [ ] Video chunks in videos bucket (if processing video)
  - [ ] Note: Audio files are not stored in Supabase

## 8. Support
For additional help:
1. Check `docs/TROUBLESHOOTING.md`
2. Review `docs/OPERATIONS.md`
3. Run verification tools with `--help` for options
