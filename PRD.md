✅ UPDATED PRD
🟪 SELF CAST STUDIOS – APP 1: TRANSCRIPT BUILDER
Module 1 of 6 → Now includes future handoff support for App 4 (Video Agent)
Updated to support video chunk extraction for dynamic media generation

1. PURPOSE
This app receives a recorded workshop interview .mp4 and transforms it into:

Clean, question-matched .md transcript chunks

Complete metadata and embeddings for vector search

Time-aligned video segment slices (saved as .mp4 clips) used later in content/video production

It serves both content generation (text) and video repurposing (media).

2. INPUTS
input.mp4: 1–3 hour video of a 2-person interview

core_workshop_questions_v1.json: 20 foundational questions used in every workshop

CATEGORY_QUESTIONS.json: 10–12 additional questions depending on client_category

client_category: One of:

narrative_defense

narrative_elevation

narrative_transition

3. OUTPUTS
✅ Textual
transcript_chunks.md: Markdown transcript divided into chunks by matched question

chunk_metadata.json: Metadata per chunk — question_id, timestamps, speaker, etc.

chunk_vectors.json: Open-source model embeddings for each chunk

errors.log: All non-breaking match/transcription issues

✅ NEW – Video
video_chunks/: Folder containing .mp4 video segments named:

Copy
Edit
Q01_identity_discovery.mp4  
Q02_turning_point.mp4  
Q03_values_shift.mp4  
Each file must match the question-aligned chunk timestamps.

video_index.json: Log linking chunk_id → video_filename → timestamp_start / end

4. LOGIC FLOW
1. AUDIO CONVERSION
Use ffmpeg to extract audio.wav from input.mp4

2. TRANSCRIPTION
Use faster-whisper with speaker diarization

Parse output: full timestamps + speaker roles

3. LOAD QUESTION BANK
Load and merge core_workshop_questions.json + appropriate category JSON

Generate embeddings for each

4. QUESTION MATCHING (Cosine Similarity)
For each interviewer line, embed → compare with all questions

If similarity > 0.80 → assign question ID → start new chunk

Group following client responses until next match

5. BUILD TEXTUAL OUTPUTS
Format .md chunks:

markdown
Copy
Edit
## [Q04] Breaking Point  
**Matched Question**: What moment forced a change?  
**Timestamp**: 00:14:32 — 00:17:01  
> Speaker 1: “I remember sitting alone…”
Write chunk_metadata.json and chunk_vectors.json

6. NEW: VIDEO SEGMENT EXPORT
For each identified chunk:

Use ffmpeg to trim input.mp4 from start_time to end_time

Save to /video_chunks/ as chunk_id.mp4

Log mapping to video_index.json:

json
Copy
Edit
{
  "chunk_id": "chunk_004",
  "question_id": "Q04",
  "video_file": "chunk_004.mp4",
  "start": "00:14:32",
  "end": "00:17:01"
}
7. ERROR LOGGING
Log missing matches or similarity < 0.80

Log transcription skips, bad speaker tags, or video export issues

5. SYSTEM CONSTRAINTS
All transcript and video chunks must be aligned by timestamp

No subtitle, watermark, or alteration of video allowed

If video export fails → do not block .md or metadata outputs

The app must remain callable as:

bash
Copy
Edit
python transcript_builder.py --mp4 input.mp4 --category narrative_elevation
6. POSTCONDITIONS
Upon completion, working directory must include:

/output/

transcript_chunks.md

chunk_metadata.json

chunk_vectors.json

errors.log

/video_chunks/

e.g., chunk_001.mp4, chunk_002.mp4

video_index.json