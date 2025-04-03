"""
Question Loader Module

This module handles loading and combining interview questions from multiple JSON files:
- core_workshop_questions.json (loaded for every interview)
- category-specific questions based on the --category flag:
  - narrative_defense_questions.json
  - narrative_elevation_questions.json
  - narrative_transition_questions.json
"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path

class QuestionLoadError(Exception):
    """Raised when there's an error loading question files"""
    pass

def load_questions(category: str, data_dir: str | Path) -> List[Dict[str, Any]]:
    """
    Load and combine core workshop questions with category-specific questions.
    
    Args:
        category: The category of questions to load ('narrative_defense', 
                 'narrative_elevation', or 'narrative_transition')
        data_dir: Path to the directory containing question JSON files
        
    Returns:
        List[Dict]: Combined list of questions from both files
        
    Raises:
        QuestionLoadError: If required files are missing or invalid
    """
    data_dir = Path(data_dir)
    
    # Validate category
    valid_categories = ['narrative_defense', 'narrative_elevation', 'narrative_transition']
    if category not in valid_categories:
        raise QuestionLoadError(
            f"Invalid category: {category}. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Load core questions (required for all interviews)
    core_path = data_dir / 'core_workshop_questions.json'
    if not core_path.exists():
        raise QuestionLoadError(f"Core questions file not found: {core_path}")
    
    try:
        with open(core_path, 'r', encoding='utf-8') as f:
            core_questions = json.load(f)
    except json.JSONDecodeError as e:
        raise QuestionLoadError(f"Error parsing core questions: {e}")
    
    # Load category-specific questions
    category_path = data_dir / f'{category}_questions.json'
    if not category_path.exists():
        raise QuestionLoadError(f"Category questions file not found: {category_path}")
    
    try:
        with open(category_path, 'r', encoding='utf-8') as f:
            category_questions = json.load(f)
    except json.JSONDecodeError as e:
        raise QuestionLoadError(f"Error parsing category questions: {e}")
    
    # Combine questions
    all_questions = core_questions + category_questions
    
    # Validate combined questions have required fields
    required_fields = ['id', 'label', 'group', 'question', 'tips', 'tags']
    for q in all_questions:
        missing_fields = [f for f in required_fields if f not in q]
        if missing_fields:
            raise QuestionLoadError(
                f"Question {q.get('id', 'unknown')} missing required fields: {missing_fields}"
            )
    
    return all_questions
