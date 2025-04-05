from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Set
import os
import json
import uuid
from datetime import datetime
from app.services.llm_service import LLMService
from app.models.game import GameState as GameStateModel
from app.models.game import World, Player

router = APIRouter()
llm_service = LLMService()

class GenerateWorldRequest(BaseModel):
    prompt: str
    
class ProcessInputRequest(BaseModel):
    input: str
    game_state: Dict[str, Any]
    chat_history: List[Dict[str, str]]
    
class ValidateJapaneseRequest(BaseModel):
    text: str
    
class GameState(BaseModel):
    state: Dict[str, Any]
    chat_history: List[Dict[str, str]]
    
class GameStateResponse(BaseModel):
    world: Dict[str, Any] = Field(default_factory=dict)
    player: Dict[str, Any] = Field(default_factory=dict)
    visited_locations: List[str] = Field(default_factory=list)
    flags: Dict[str, bool] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class WorldResponse(BaseModel):
    world: Dict[str, Any]
    
class ProcessInputResponse(BaseModel):
    response: str
    game_state: Dict[str, Any]
    chat_history: List[Dict[str, str]]
    
class ValidateJapaneseResponse(BaseModel):
    is_valid: bool
    feedback: str

class SaveGameRequest(BaseModel):
    state: Dict[str, Any]
    chat_history: List[Dict[str, str]]

class SaveGameResponse(BaseModel):
    status: str
    message: str
    game_id: Optional[str] = None

class LoadGameRequest(BaseModel):
    game_id: str

class LoadGameResponse(BaseModel):
    state: Dict[str, Any]
    chat_history: List[Dict[str, str]]

@router.post("/generate-world", response_model=WorldResponse)
async def generate_world(request: GenerateWorldRequest):
    """Generate a new game world based on the provided prompt"""
    try:
        world_data = await llm_service.generate_world(request.prompt)
        return WorldResponse(world=world_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate world: {str(e)}")

@router.post("/process-input", response_model=ProcessInputResponse)
async def process_input(request: ProcessInputRequest):
    """Process player input and return game response"""
    try:
        response, updated_state = await llm_service.process_game_input(
            request.input,
            request.game_state,
            request.chat_history
        )
        
        # Update chat history
        updated_chat_history = request.chat_history + [
            {"role": "user", "content": request.input},
            {"role": "assistant", "content": response}
        ]
        
        return ProcessInputResponse(
            response=response,
            game_state=updated_state,
            chat_history=updated_chat_history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process input: {str(e)}")

@router.post("/validate-japanese", response_model=ValidateJapaneseResponse)
async def validate_japanese(request: ValidateJapaneseRequest):
    """Validate Japanese text input"""
    try:
        is_valid, feedback = await llm_service.validate_japanese(request.text)
        return ValidateJapaneseResponse(
            is_valid=is_valid,
            feedback=feedback
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate text: {str(e)}")

@router.post("/save-state", response_model=SaveGameResponse)
async def save_game_state(request: SaveGameRequest):
    """Save the current game state"""
    try:
        # Create a save directory if it doesn't exist
        save_dir = os.path.join(os.getcwd(), "game_saves")
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate a unique ID for the save file
        game_id = str(uuid.uuid4())
        
        # Create a save file with the state and chat history
        save_data = {
            "state": request.state,
            "chat_history": request.chat_history,
            "timestamp": datetime.now().isoformat()
        }
        
        save_path = os.path.join(save_dir, f"{game_id}.json")
        
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2)
        
        return SaveGameResponse(
            status="success",
            message="Game state saved successfully",
            game_id=game_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save game state: {str(e)}")

@router.post("/load-state", response_model=LoadGameResponse)
async def load_game_state(request: LoadGameRequest):
    """Load a saved game state"""
    try:
        # Find the save file
        save_dir = os.path.join(os.getcwd(), "game_saves")
        save_path = os.path.join(save_dir, f"{request.game_id}.json")
        
        if not os.path.exists(save_path):
            raise HTTPException(status_code=404, detail=f"Save file with ID {request.game_id} not found")
        
        # Load the save file
        with open(save_path, "r") as f:
            save_data = json.load(f)
        
        return LoadGameResponse(
            state=save_data["state"],
            chat_history=save_data["chat_history"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load game state: {str(e)}")

@router.get("/saved-games")
async def list_saved_games():
    """List all saved games"""
    try:
        # Find all save files
        save_dir = os.path.join(os.getcwd(), "game_saves")
        
        if not os.path.exists(save_dir):
            return {"saved_games": []}
        
        saved_games = []
        
        for filename in os.listdir(save_dir):
            if filename.endswith(".json"):
                save_path = os.path.join(save_dir, filename)
                
                try:
                    with open(save_path, "r") as f:
                        save_data = json.load(f)
                        
                    game_id = filename.replace(".json", "")
                    
                    # Extract some basic info about the save
                    player_location = save_data["state"]["player"]["current_location"]
                    location_name = "Unknown"
                    
                    if "world" in save_data["state"] and "locations" in save_data["state"]["world"]:
                        location_data = save_data["state"]["world"]["locations"].get(player_location, {})
                        location_name = location_data.get("name", "Unknown")
                    
                    saved_games.append({
                        "game_id": game_id,
                        "timestamp": save_data.get("timestamp", "Unknown"),
                        "location": location_name,
                        "player_stats": save_data["state"]["player"].get("stats", {})
                    })
                except Exception as e:
                    # Skip invalid save files
                    print(f"Error reading save file {filename}: {str(e)}")
        
        return {"saved_games": saved_games}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list saved games: {str(e)}")

@router.get("/commands", response_model=Dict[str, List[str]])
async def get_available_commands():
    """Get a list of available game commands"""
    return {
        "movement": ["north", "south", "east", "west", "up", "down", "in", "out"],
        "actions": ["look", "examine", "take", "drop", "inventory", "use", "talk", "help"],
        "japanese_commands": ["見る", "調べる", "持つ", "取る", "拾う", "置く", "捨てる", "持ち物", "使う", "話す", "聞く", "質問", "助け", "ヘルプ"]
    } 