from typing import List, Dict, Any
import re
from pydantic import BaseModel, Field

# Import our custom client
from tools.custom_client import CustomOllamaClient

# Import prompts
from prompts import VOCABULARY_EXTRACTION_PROMPT

# Configure our custom client
custom_client = CustomOllamaClient(host="http://localhost:9000")

class Part(BaseModel):
    kanji: str = Field(..., description="A character or part of the word")
    romaji: List[str] = Field(..., description="Romanized pronunciation of this part")

class VocabularyItem(BaseModel):
    kanji: str = Field(..., description="The original word in Japanese characters")
    romaji: str = Field(..., description="The romanized pronunciation of the word")
    english: str = Field(..., description="The English translation of the word")
    parts: List[Part] = Field(..., description="The individual parts of the word with their readings")

class VocabularyList(BaseModel):
    items: List[VocabularyItem] = Field(..., description="List of vocabulary items extracted from the lyrics")

def extract_vocabulary(lyrics: str, max_items: int = None) -> List[Dict[str, Any]]:
    """
    Extract all vocabulary items from lyrics using structured output.
    """
    prompt = VOCABULARY_EXTRACTION_PROMPT.format(
        lyrics=lyrics
    )
    
    try:
        # Use our custom client to get structured output
        response = custom_client.generate_structured(
            model="llama3.1:8b",
            prompt=prompt,
            response_model=VocabularyList,
            max_tokens=4096,
        )
        
        return [item.model_dump() for item in response.items]
    except Exception as e:
        # Fallback for errors
        return [{
            "error": f"Error extracting vocabulary: {str(e)}",
            "kanji": "エラー",
            "romaji": "erā",
            "english": "error",
            "parts": [
                {"kanji": "エ", "romaji": ["e"]},
                {"kanji": "ラー", "romaji": ["rā"]}
            ]
        }] 