-- Get table structure
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    column_default,
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_name = 'chunks';

-- Get sample of existing data
SELECT 
    id,
    chunk_id,
    question_id,
    question_text,
    response_text,
    start_time,
    end_time,
    similarity_score,
    project_id,
    user_id,
    created_at
FROM chunks
LIMIT 5;

-- Get count of chunks
SELECT COUNT(*) as total_chunks FROM chunks;

-- Get unique projects
SELECT DISTINCT project_id 
FROM chunks 
WHERE project_id IS NOT NULL;
