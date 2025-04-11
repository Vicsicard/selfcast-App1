# Transcript Builder Troubleshooting Guide

## Quick Reference

| Issue | Check | Solution |
|-------|--------|----------|
| Python version mismatch | `python --version` | Switch to Python 3.10 |
| Supabase connection | Check .env | Update credentials |
| File processing error | Check logs | See specific error section |

## Common Issues & Solutions

### 1. Environment Setup

#### Python Version Issues
```bash
Error: ImportError: cannot import name 'X' from 'Y'
```
**Solution:**
1. Verify Python version:
   ```bash
   python --version  # Should be 3.10.x
   ```
2. Recreate virtual environment:
   ```bash
   rm -rf venv310
   python -m venv venv310
   source venv310/Scripts/activate
   pip install -r requirements.txt
   ```

### 2. Supabase Integration

#### Connection Errors
```bash
Error: Unable to connect to Supabase
```
**Solution:**
1. Check .env configuration
2. Verify network connectivity
3. Validate credentials:
   ```bash
   python -c "from utils.supabase_client import get_client; print(get_client().auth.get_session())"
   ```

### 3. File Processing

#### VTT Processing Errors
```bash
Error: Invalid VTT format
```
**Solution:**
1. Verify VTT file format
2. Check for UTF-8 encoding
3. Validate timestamps

#### MP4 Processing Errors
```bash
Error: FFmpeg processing failed
```
**Solution:**
1. Check FFmpeg installation
2. Verify MP4 file integrity
3. Check available disk space

### 4. Output Validation

#### Missing Output Files
**Solution:**
1. Check process completion in logs
2. Verify write permissions
3. Check available disk space

#### Invalid Markdown Format
**Solution:**
1. Review input file formatting
2. Check for processing errors
3. Validate chunk processing

## Logging

### Log Locations
1. Main log: `output/[job_id]/errors.log`
2. Supabase logs: Check Supabase dashboard
3. Process logs: Terminal output

### Log Analysis
1. Check timestamp of error
2. Look for related errors
3. Review full process context

## Recovery Procedures

### 1. Failed Uploads
1. Check `transcript_files` table
2. Verify file existence
3. Retry upload:
   ```bash
   python utils/supabase_upload.py --retry [job_id]
   ```

### 2. Corrupted Output
1. Clear output directory
2. Rerun processing
3. Verify new output

## Contact Support

If issues persist:
1. Document exact error
2. Collect relevant logs
3. Contact development team

---

Last Updated: 2025-04-10
