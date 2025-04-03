"""Test the chunking, embedding, and Supabase pipeline."""
import json
import os
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client
from sentence_transformers import SentenceTransformer
import uuid

def load_questions(category="core_workshop"):
    """Load questions from the specified category."""
    with open(f"data/{category}_questions.json", "r") as f:
        return json.load(f)

def load_transcript():
    """Load the sample transcript."""
    with open("data/sample_transcript.json", "r") as f:
        return json.load(f)

def find_best_matching_question(text, questions, model):
    """Find the best matching question for a given text segment."""
    text_embedding = model.encode(text, convert_to_tensor=False)
    best_score = -1
    best_question = None
    
    for question in questions:
        question_embedding = model.encode(question["question"], convert_to_tensor=False)
        similarity = compute_similarity(text_embedding, question_embedding)
        if similarity > best_score:
            best_score = similarity
            best_question = question
    
    return best_question, best_score

def compute_similarity(embedding1, embedding2):
    """Compute cosine similarity between two embeddings."""
    import numpy as np
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def main():
    """Run the test pipeline."""
    # Load environment variables
    load_dotenv()
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    # Initialize the embedding model
    logger.info("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load questions and transcript
    questions = load_questions()
    transcript = load_transcript()
    
    # Process each segment
    for segment in transcript["segments"]:
        # Find best matching question
        question, similarity_score = find_best_matching_question(segment["text"], questions, model)
        
        if similarity_score < 0.5:  # Skip if no good match found
            logger.warning(f"No good match found for segment: {segment['text'][:50]}...")
            continue
            
        # Generate embedding for the response
        embedding = model.encode(segment["text"], convert_to_tensor=False).tolist()
        
        # Create chunk data
        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "question_id": question["id"],
            "question_text": question["question"],
            "response_text": segment["text"],
            "start_time": str(segment["start"]),
            "end_time": str(segment["end"]),
            "similarity_score": float(similarity_score),
            "vector_embedding": embedding,
            "project_id": "test_project",
            "user_id": "test_user"
        }
        
        # Insert into Supabase
        logger.info(f"Inserting chunk for question {question['id']}...")
        result = supabase.table("chunks").insert(chunk).execute()
        
        # Log the match
        logger.info(f"Matched Q{question['id']}: {question['label']}")
        logger.info(f"Similarity score: {similarity_score:.2f}")
        logger.info("---")

if __name__ == "__main__":
    main()
