# Transcript Builder Operations Manual

🚨 **CRITICAL REQUIREMENT: This application MUST run on Python 3.10 ONLY** 🚨

## Table of Contents
1. [Setup & Prerequisites](#setup--prerequisites)
2. [Directory Structure](#directory-structure)
3. [Processing Workflows](#processing-workflows)
4. [Quality Control](#quality-control)
5. [Troubleshooting](#troubleshooting)

## Setup & Prerequisites

### 1. Python Environment
```bash
# Create Python 3.10 virtual environment
python -m venv venv310
source venv310/Scripts/activate  # Windows: .\venv310\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### First Action - Always Check Python Version
```bash
python --version  # MUST show Python 3.10.x
```
⛔ If NOT Python 3.10.x:
1. STOP immediately
2. Switch to Python 3.10
3. Do not proceed until Python 3.10 is active

### 2. Environment Configuration
1. Copy `.env.example` to `.env`
2. Configure Supabase credentials:
   ```env
   SUPABASE_URL=your_url
   SUPABASE_SERVICE_ROLE_KEY=your_key
   ```

### 3. Directory Structure Verification
```
self-cast-studio-app-1/
├── docs/               # Documentation
├── input/             # Source VTT/MP4 files
├── output/            # Processed transcripts
├── utils/             # Processing utilities
└── tests/             # Test files
```

## Processing Workflows

### VTT Mode
For processing with existing VTT transcripts:

1. Place VTT file in `input/` directory
2. Run command:
   ```bash
   python transcript_builder.py \
     --vtt input/your_file.vtt \
     --category narrative_defense \
     --output-dir output \
     --project-id your_project_id \
     --user-id your_user_id
   ```

### MP4 Mode
For processing video files with Whisper transcription:

1. Place MP4 file in `input/` directory
2. Run command:
   ```bash
   python transcript_builder.py \
     --mp4 input/your_file.mp4 \
     --category narrative_defense \
     --output-dir output \
     --project-id your_project_id \
     --user-id your_user_id
   ```

## Quality Control

### 1. Output Verification
Check for these files in `output/[job_id]/`:
- `transcript_chunks/*.md` - Individual transcript chunks
- `chunk_metadata.json` - Segment metadata
- `errors.log` - Processing errors

### 2. Supabase Verification
1. Check Storage buckets:
   - `videos/` - For MP4 files
   - `documents/` - For MD and JSON files
2. Verify `transcript_files` table entry

### 3. Error Checking
1. Review `output/[job_id]/errors.log`
2. Check Supabase upload status
3. Verify chunk processing completion

## Troubleshooting

### Common Issues

1. **Python Environment Issues**
   - Ensure Python 3.10 is active
   - Reinstall dependencies if needed

2. **Supabase Connection**
   - Verify .env configuration
   - Check network connectivity
   - Validate credentials

3. **Processing Errors**
   - Check input file format
   - Verify file permissions
   - Review error logs

### Support

For additional issues:
1. Check `TROUBLESHOOTING.md`
2. Review GitHub issues
3. Contact development team

## Mandatory Procedures

1. **Always** follow this workflow exactly
2. **Never** skip verification steps
3. **Document** any new issues
4. **Update** this guide as needed

---

Last Updated: 2025-04-10
