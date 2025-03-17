# This file makes the prompts directory a Python package
from .agent_prompts import REACT_AGENT_PROMPT
from .song_metadata_prompt import SONG_METADATA_PROMPT
from .vocabulary_extraction_prompt import VOCABULARY_EXTRACTION_PROMPT

__all__ = [
    'REACT_AGENT_PROMPT',
    'SONG_METADATA_PROMPT',
    'VOCABULARY_EXTRACTION_PROMPT'
] 