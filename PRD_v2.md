# ✅ UPDATED PRD
# 🟪 SELF CAST STUDIOS – APP 1: TRANSCRIPT BUILDER
Module 1 of 6 → Now includes future handoff support for App 4 (Video Agent)  
Updated to support clean Speaker 2 chunk extraction for dynamic media and text generation

## 1. PURPOSE
This app receives an interview package consisting of a .mp4 video, .vtt subtitle file, and a matching .m4a audio file. It processes this into:
* Clean markdown transcript chunks based only on Speaker 2 responses
* Video/audio segments of those responses, timestamp-aligned to the .vtt
* Subtitle segments that match each chunk
* Structured metadata for use in downstream apps

It enables both authentic shortform video creation (App 4) and deep narrative content analysis (App 2, App 3).

## 2. INPUTS
| File | Description |
|------|-------------|
| input.mp4 | Full recorded workshop interview |
| input.vtt | Subtitle file with full timestamps and speakers |
| input.m4a | Audio-only version, exactly matches .mp4 |

❗️Interview format assumes Speaker 1 = interviewer, Speaker 2 = subject (target voice)

## 3. OUTPUTS
### ✅ Textual
* transcript_chunks.md: Markdown transcript, divided into timestamped Speaker 2-only chunks
* chunk_metadata.json: Start/end times, chunk duration, raw transcript per chunk
* chunk_vectors.json: Embeddings for each chunk for later use in vector search and App 2/3

### ✅ Video
* /video_chunks/: Trimmed .mp4 files of each Speaker 2 chunk
* /audio_chunks/: Trimmed .m4a files of each Speaker 2 chunk
* /subtitles_chunks/: Trimmed .vtt files of each Speaker 2 chunk
* video_index.json: Maps each chunk to its video/audio file and timestamps

## 4. LOGIC FLOW
### 1. PARSE .vtt
* Read and extract Speaker 2-only segments with full timestamps
* Group contiguous Speaker 2 lines into coherent chunks (≤ 30 seconds preferred)

### 2. BUILD TRANSCRIPT CHUNKS
Create markdown block per chunk:
```markdown
## [Chunk 05]
**Timestamp**: 00:11:30 — 00:12:04  
> Speaker 2: I kept showing up, even when I had no idea what I was doing.
```

### 3. GENERATE METADATA
chunk_metadata.json captures:
* chunk_id
* start/end
* raw text
* speaker tag (always Speaker 2)
* chunk_vectors.json: Embeddings per chunk (optional for now)

### 4. TRIM VIDEO/AUDIO/SUBTITLES
Use ffmpeg to extract:
* .mp4 chunk from input.mp4
* .m4a chunk from input.m4a
* .vtt chunk from input.vtt

Name outputs:
* chunk_001.mp4
* chunk_001.m4a
* chunk_001.vtt

### 5. INDEX CHUNKS
Build video_index.json like:
```json
{
  "chunk_id": "chunk_001",
  "video_file": "chunk_001.mp4",
  "audio_file": "chunk_001.m4a",
  "subtitle_file": "chunk_001.vtt",
  "start": "00:11:30",
  "end": "00:12:04"
}
```

### 6. LOG ERRORS
errors.log tracks:
* Any skipped segments (empty text, faulty timestamps)
* Chunking issues
* ffmpeg errors

## 5. SYSTEM CONSTRAINTS
* Speaker 2 chunks only — no inclusion of Speaker 1 content
* .vtt is the authoritative source for transcript and timing
* Outputs must be timestamp-synchronized across video, audio, and subtitle
* Video/audio slicing must not modify original content (no watermark, no re-encoding effects)
* Chunk duration ideally ≤ 30 seconds, with padding allowed if context helps

## 6. POSTCONDITIONS
Upon successful execution, the app must create an /output/ folder with:
```
/output/
├── transcript_chunks.md
├── chunk_metadata.json
├── chunk_vectors.json
├── errors.log
├── video_index.json
├── /video_chunks/
│   ├── chunk_001.mp4
│   ├── chunk_002.mp4
├── /audio_chunks/
│   ├── chunk_001.m4a
│   ├── chunk_002.m4a
├── /subtitles_chunks/
│   ├── chunk_001.vtt
│   ├── chunk_002.vtt
```

This revised PRD reflects your current streamlined approach: Speaker 2-only analysis, no question matching, shortform-first priorities, and clean multimodal output alignment for downstream use in App 2–4.
