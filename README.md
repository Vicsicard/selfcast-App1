# Transcript Builder

A Python-based command-line tool that converts video interviews into structured markdown transcripts, with semantic matching and vector storage capabilities.

## Features

- 🎥 Video to text transcription (using faster-whisper)
- 🔍 Semantic matching of responses to predefined questions
- 📊 Vector embeddings generation using sentence-transformers
- 💾 Vector storage in Supabase
- 📝 Markdown transcript generation

## Project Structure

```
transcript-builder/
├── audio/              # Temporary audio files
├── data/               # Question banks and sample data
│   ├── core_workshop_questions.json
│   ├── narrative_defense_questions.json
│   └── sample_transcript.json
├── input/              # Input video files
├── migrations/         # Database migrations
├── output/            # Generated transcripts
├── tests/             # Test files
└── utils/             # Utility modules
```

## Prerequisites

- Python 3.11+
- FFmpeg (for audio extraction)
- Supabase account and project

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/transcript-builder.git
cd transcript-builder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Supabase credentials:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_PROJECT_ID=your_project_id
SUPABASE_ANON_KEY=your_anon_key
```

## Usage

1. Place your MP4 interview file in the `input` directory

2. Run the transcript builder:
```bash
python transcript_builder.py --mp4 input/your_video.mp4 --category core_workshop
```

Available categories:
- core_workshop
- narrative_defense
- narrative_elevation
- narrative_transition

## Database Schema

The `chunks` table in Supabase stores:
- Transcript chunks with timestamps
- Question matches and similarity scores
- 384-dimension vector embeddings
- Project and user metadata

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Key test files:
- `test_env.py`: Environment variable validation
- `test_supabase.py`: Supabase connection testing
- `test_pipeline.py`: End-to-end pipeline testing

## Development

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dev dependencies:
```bash
pip install -r requirements.txt
```

### Adding New Question Categories

1. Create a new JSON file in `data/` following the existing format
2. Update the category validation in `transcript_builder.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License

## Acknowledgments

- [sentence-transformers](https://www.sbert.net/) for embeddings
- [Supabase](https://supabase.com/) for vector storage
- [FFmpeg](https://ffmpeg.org/) for audio processing
