PRD: 
🟪 SELF CAST STUDIOS – APP 1: TRANSCRIPT BUILDER
Module 1 of 6 in the Self Cast Studios system
 App Function: Converts .mp4 client interviews into structured, vector-ready .md transcript chunks for downstream processing.

1. PURPOSE
This app receives a recorded workshop interview (.mp4) and transforms it into a clean, chronologically segmented .md transcript. The transcript must be broken into narrative chunks based on a fixed workshop question set. The result must include complete metadata for downstream processing, including timestamps, matched question ID, speaker roles, and embeddings.

2. INPUTS
input.mp4: 1–3 hour video of a 2-person interview (interviewer + client)


core_workshop_questions_v1.json: A list of 20 fixed workshop questions used in every interview


CATEGORY_QUESTIONS.json: An additional 10–12 questions based on one of three client types: narrative_defense, narrative_transition, or narrative_elevation


client_category: A string that determines which category-specific JSON to load



3. OUTPUTS
transcript_chunks.md: Clean Markdown file, divided by matched workshop questions


chunk_metadata.json: Metadata for each chunk (chunk_id, question_id, start_time, end_time, speaker_tags, similarity_score)


chunk_vectors.json: Embeddings for each chunk for vector retrieval systems


errors.log: List of non-breaking errors (e.g., unmatched questions, confidence below threshold)



4. LOGIC FLOW (DO EXACTLY AS WRITTEN)
1. AUDIO CONVERSION
Use ffmpeg to extract audio from input.mp4


Save output as audio.wav


2. TRANSCRIPTION
Use faster-whisper with speaker diarization enabled


Output must include full timestamps and distinct speaker tags (Speaker 0, Speaker 1)


3. LOAD QUESTION BANK
Load core_workshop_questions_v1.json


Load the category file that matches client_category


Combine the 20 core and category-specific questions into a single reference list


Generate an embedding for each question using text-embedding-ada-002 (OpenAI)


4. MATCH QUESTIONS TO INTERVIEW PROMPTS
Loop through every interviewer segment in the transcript


Generate embeddings for each interviewer line


Calculate cosine similarity against every workshop question


Match the question with the highest similarity score above 0.8


If a match is found, this begins a new chunk


Group all client responses until the next question match


5. BUILD OUTPUT FILES
Format each chunk as a section in transcript_chunks.md


Use matched question label as ## header


Include timestamp, chunk_id, and matched_question below header


Format all client responses as clean blockquotes


Write each chunk’s metadata (question ID, timestamps, similarity score) to chunk_metadata.json


Write each chunk’s embedding to chunk_vectors.json


6. LOG ERRORS
If no match is found above threshold, log that line in errors.log


Log transcription or diarization issues if they occur



5. SYSTEM CONSTRAINTS
Do not generate output if any of the input files are missing


Do not modify or rephrase any client responses


Do not change the formatting conventions of the .md structure


The app must be callable as a CLI tool using one command:


bash
CopyEdit
python transcript_builder.py --mp4 input.mp4 --category narrative_defense


6. POSTCONDITIONS
When the app finishes, the working directory must contain:
transcript_chunks.md


chunk_metadata.json


chunk_vectors.json


errors.log (can be empty)


No other output is permitted.

