-- Create transcript_files table for storing file metadata
create table transcript_files (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  transcript_id uuid not null,
  file_type text,
  file_name text,
  file_path text,
  bucket text,
  uploaded_at timestamp default now()
);

-- Enable RLS
alter table transcript_files enable row level security;

-- Add RLS policy for user access
create policy "Allow user to access their own files"
  on transcript_files
  for all
  using (auth.uid() = user_id);
