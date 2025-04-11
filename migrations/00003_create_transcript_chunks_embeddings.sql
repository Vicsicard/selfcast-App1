-- Create transcript_chunks_embeddings table
CREATE TABLE transcript_chunks_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transcript_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL,  -- Using pgvector for embeddings
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    speaker TEXT,
    video_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

-- Create index for similarity search
CREATE INDEX ON transcript_chunks_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Add RLS policies
ALTER TABLE transcript_chunks_embeddings ENABLE ROW LEVEL SECURITY;

-- Users can read their own transcript chunks
CREATE POLICY "Users can read own transcript chunks"
    ON transcript_chunks_embeddings
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own transcript chunks
CREATE POLICY "Users can insert own transcript chunks"
    ON transcript_chunks_embeddings
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own transcript chunks
CREATE POLICY "Users can update own transcript chunks"
    ON transcript_chunks_embeddings
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own transcript chunks
CREATE POLICY "Users can delete own transcript chunks"
    ON transcript_chunks_embeddings
    FOR DELETE
    USING (auth.uid() = user_id);
