import re
import os
import json
import uuid
import time
import traceback
from typing import List, Dict, Any, Callable, Optional
from pydantic import BaseModel, Field

# Import tools
from tools.extract_vocabulary import extract_vocabulary
from tools.get_page_content import get_page_content
from tools.search_web import search_web
from tools.custom_client import CustomOllamaClient

# Import prompts
from prompts import REACT_AGENT_PROMPT, SONG_METADATA_PROMPT

# Configure Ollama with our custom client
custom_client = CustomOllamaClient(host="http://localhost:9000")

# Ensure outputs directory exists
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

class Part(BaseModel):
    kanji: str = Field(..., description="A character or part of the word")
    romaji: List[str] = Field(..., description="Romanized pronunciation of this part")

class VocabularyItem(BaseModel):
    kanji: str = Field(..., description="The original word in Japanese characters")
    romaji: str = Field(..., description="The romanized pronunciation of the word")
    english: str = Field(..., description="The English translation of the word")
    parts: List[Part] = Field(..., description="The individual parts of the word with their readings")

class AgentOutput(BaseModel):
    lyrics: str = Field(..., description="The complete lyrics of the song")
    vocabulary: List[VocabularyItem] = Field(..., description="List of vocabulary items extracted from the lyrics with kanji, romaji, english, and parts")

class AgentAction(BaseModel):
    tool: str = Field(..., description="The tool to use")
    tool_input: Dict[str, Any] = Field(..., description="The input to the tool")
    thought: str = Field(..., description="The reason for using this tool")

class AgentResponse(BaseModel):
    action: Optional[AgentAction] = Field(None, description="The next action to take")
    final_answer: Optional[AgentOutput] = Field(None, description="The final answer if the agent is done")

class SongMetadata(BaseModel):
    title: str = Field(..., description="The title of the song")
    artist: str = Field(..., description="The artist or band who performed the song")

# Define the available tools
TOOLS = {
    "search_web": search_web,
    "get_page_content": get_page_content,
    "extract_vocabulary": extract_vocabulary,
}

async def run_agent(message_request: str, max_iterations: int = 10) -> Dict[str, Any]:
    """Run the agent to find lyrics and extract vocabulary."""
    
    print(f"Starting agent with query: {message_request}")
    messages = [{"role": "system", "content": REACT_AGENT_PROMPT}]
    messages.append({"role": "user", "content": f"Find lyrics and extract vocabulary for: {message_request}"})
    
    # Agent loop
    for i in range(max_iterations):
        print(f"\n--- Iteration {i+1}/{max_iterations} ---")
        
        try:
            print("Generating agent response...")
            response = custom_client.generate_structured(
                model="llama3.1:8b",
                prompt="\n".join([msg["content"] for msg in messages]),
                response_model=AgentResponse,
                max_tokens=2048,
            )
            
            print(f"Agent response type: {type(response)}")
            print(f"Has action: {response.action is not None}")
            print(f"Has final answer: {response.final_answer is not None}")
            
            # Add the assistant's response to the message history
            messages.append({"role": "assistant", "content": json.dumps(response.model_dump())})
            
            # If we have a final answer, save it to files and return a handler
            if response.final_answer:
                print("Got final answer!")
                return save_results_to_files(message_request, response.final_answer)
                
            # If we need to take an action
            if response.action:
                action = response.action
                tool_name = action.tool
                tool_input = action.tool_input
                
                print(f"Taking action: {tool_name}")
                print(f"Tool input: {tool_input}")
                print(f"Agent thought: {action.thought}")
                
                # Execute the tool
                if tool_name in TOOLS:
                    print(f"Executing tool: {tool_name}")
                    tool_result = TOOLS[tool_name](**tool_input)
                    
                    # Truncate large results for logging
                    result_preview = str(tool_result)
                    if len(result_preview) > 500:
                        result_preview = result_preview[:500] + "... [truncated]"
                    print(f"Tool result preview: {result_preview}")
                    
                    messages.append({
                        "role": "user", 
                        "content": f"Tool result: {json.dumps(tool_result)}"
                    })
                else:
                    print(f"ERROR: Tool {tool_name} not found!")
                    messages.append({
                        "role": "user", 
                        "content": f"Error: Tool {tool_name} not found. Available tools: {', '.join(TOOLS.keys())}"
                    })
            else:
                print("WARNING: Agent provided neither action nor final answer!")
        except Exception as e:
            print(f"ERROR in iteration {i+1}: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            # Continue to next iteration despite error
    
    print("Reached maximum iterations without finding lyrics")
    
    # If we've reached the maximum number of iterations, return an error with a handler
    handler_id = str(uuid.uuid4())
    error_dir = os.path.join(OUTPUTS_DIR, handler_id)
    os.makedirs(error_dir, exist_ok=True)
    
    error_data = {
        "error": "Failed to find lyrics after maximum iterations",
        "query": message_request,
        "timestamp": time.time()
    }
    
    with open(os.path.join(error_dir, "error.json"), "w") as f:
        json.dump(error_data, f, indent=2)
        
    return {
        "handler": handler_id,
        "status": "error",
        "message": "Failed to find lyrics after maximum iterations"
    }

def save_results_to_files(query: str, results: AgentOutput) -> Dict[str, Any]:
    """Save results to files and return a handler."""
    # Generate handler ID
    handler_id = str(uuid.uuid4())
    result_dir = os.path.join(OUTPUTS_DIR, handler_id)
    os.makedirs(result_dir, exist_ok=True)
    
    # Save lyrics to a text file
    lyrics_path = os.path.join(result_dir, "lyrics.txt")
    with open(lyrics_path, "w", encoding="utf-8") as f:
        f.write(results.lyrics)
    
    # Save vocabulary to a JSON file
    vocab_path = os.path.join(result_dir, "vocabulary.json")
    with open(vocab_path, "w", encoding="utf-8") as f:
        vocab_data = [item.model_dump() for item in results.vocabulary]
        json.dump(vocab_data, f, indent=2, ensure_ascii=False)
    
    # Extract song metadata
    metadata_info = extract_song_metadata(query, results.lyrics)
    
    # Save to database and get song_id
    from db_schema import save_song_and_vocabulary
    song_id = save_song_and_vocabulary(
        title=metadata_info["title"],
        artist=metadata_info["artist"], 
        lyrics=results.lyrics,
        vocabulary=[item.model_dump() for item in results.vocabulary]
    )
    
    # Create metadata file
    metadata = {
        "query": query,
        "timestamp": time.time(),
        "lyrics_file": "lyrics.txt",
        "vocabulary_file": "vocabulary.json",
        "song_id": song_id,
        "title": metadata_info["title"],
        "artist": metadata_info["artist"]
    }
    
    with open(os.path.join(result_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    return {
        "handler": handler_id,
        "status": "success",
        "message": "Successfully retrieved lyrics and vocabulary",
        "song_id": song_id,
        "title": metadata_info["title"],
        "artist": metadata_info["artist"]
    }

def get_results_by_handler(handler_id: str) -> Dict[str, Any]:
    """Retrieve results using a handler ID."""
    result_dir = os.path.join(OUTPUTS_DIR, handler_id)
    
    if not os.path.exists(result_dir):
        return {
            "status": "error",
            "message": f"No results found for handler {handler_id}"
        }
    
    # Check for error file
    error_path = os.path.join(result_dir, "error.json")
    if os.path.exists(error_path):
        with open(error_path, "r") as f:
            return {
                "status": "error",
                "data": json.load(f)
            }
    
    # Load lyrics
    lyrics_path = os.path.join(result_dir, "lyrics.txt")
    with open(lyrics_path, "r", encoding="utf-8") as f:
        lyrics = f.read()
    
    # Load vocabulary
    vocab_path = os.path.join(result_dir, "vocabulary.json")
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocabulary = json.load(f)
    
    return {
        "status": "success",
        "lyrics": lyrics,
        "vocabulary": vocabulary
    }

def extract_song_metadata(query: str, lyrics: str) -> Dict[str, str]:
    """
    Extract song title and artist from the query and lyrics.
    """
    prompt = SONG_METADATA_PROMPT.format(
        query=query,
        lyrics_excerpt=lyrics[:500]
    )
    
    try:
        response = custom_client.generate_structured(
            model="llama3.1:8b",
            prompt=prompt,
            response_model=SongMetadata,
            max_tokens=256,
        )
        return response.model_dump()
    except Exception as e:
        # Fallback: use query as title if extraction fails
        return {
            "title": query,
            "artist": "Unknown"
        }

# Add this function to fix vocabulary items with missing parts
def fix_vocabulary_format(data):
    """Ensure all vocabulary items have the required fields including parts."""
    if not data or not isinstance(data, dict):
        return data
        
    # If this is the final answer with vocabulary
    if "final_answer" in data and isinstance(data["final_answer"], dict):
        final_answer = data["final_answer"]
        
        # If it has vocabulary items
        if "vocabulary" in final_answer and isinstance(final_answer["vocabulary"], list):
            for i, item in enumerate(final_answer["vocabulary"]):
                # Ensure each item has kanji, romaji, english
                if "kanji" not in item or not item["kanji"]:
                    item["kanji"] = f"未知{i+1}"  # Unknown + number
                
                if "romaji" not in item or not item["romaji"]:
                    if "kanji" in item and item["kanji"]:
                        item["romaji"] = item["kanji"]  # Use kanji as fallback
                    else:
                        item["romaji"] = f"michi{i+1}"  # Unknown in romaji
                
                if "english" not in item or not item["english"]:
                    item["english"] = f"unknown term {i+1}"
                
                # Add parts if missing
                if "parts" not in item or not isinstance(item["parts"], list) or not item["parts"]:
                    # Create a simple part from the whole word
                    item["parts"] = [{
                        "kanji": item["kanji"],
                        "romaji": [item["romaji"] if isinstance(item["romaji"], str) else item["romaji"][0]]
                    }]
                    
                # Ensure each part has required fields
                for part in item["parts"]:
                    if "kanji" not in part or not part["kanji"]:
                        part["kanji"] = item["kanji"]
                    
                    if "romaji" not in part or not part["romaji"]:
                        if isinstance(item["romaji"], list):
                            part["romaji"] = item["romaji"]
                        else:
                            part["romaji"] = [item["romaji"]] 