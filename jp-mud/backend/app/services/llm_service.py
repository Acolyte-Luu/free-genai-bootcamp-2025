import json
import os
import re
import requests
from typing import Dict, List, Tuple, Any, Optional
import asyncio
from loguru import logger
import aiohttp
import ast  # For literal_eval as a last-resort parser
from app.services.game_engine import GameEngine
from app.models.game import GameState
from app.services.world_templates import DEFAULT_WORLD
from app.services.quest_templates import DEFAULT_QUESTS, QUEST_ITEMS, HIDDEN_LOCATIONS

def clean_json_string(json_str: str) -> str:
    """Clean a JSON string by removing control characters and other problematic content"""
    # Remove markdown code block markers
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    elif json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    
    # Trim whitespace
    json_str = json_str.strip()
    
    # Handle common issues with raw string literals
    # Replace literal \n with actual newlines before processing
    json_str = json_str.replace('\\n', '\n')
    json_str = json_str.replace('\\r', '\r')
    json_str = json_str.replace('\\t', '\t')
    
    # Process the string character by character
    result = []
    i = 0
    while i < len(json_str):
        char = json_str[i]
        
        # Check for raw control characters (not escaped sequences)
        if char in '\n\r\t':
            # Replace with JSON-compatible space
            result.append(' ')
        elif ord(char) < 32:
            # Skip other control characters
            pass
        else:
            # Keep printable characters
            result.append(char)
        
        i += 1
    
    cleaned = ''.join(result)
    
    # Standardize quotes (in case smart quotes were used)
    cleaned = cleaned.replace('"', '"').replace('"', '"')
    
    return cleaned

def extreme_json_clean(text: str) -> str:
    """
    Last-resort JSON cleaning that attempts to extract and reconstruct a valid JSON structure
    """
    # First, ensure literal newlines are properly handled
    text = text.replace('\\n', ' ')
    text = text.replace('\\r', ' ')
    text = text.replace('\\t', ' ')
    
    # Replace actual newlines and tabs with spaces (safer for JSON)
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')
    
    # Remove all whitespace outside of quoted strings
    in_string = False
    result = []
    for char in text:
        if char == '"' and (not result or result[-1] != '\\'):
            in_string = not in_string
            result.append(char)
        elif in_string or not char.isspace():
            result.append(char)
    
    cleaned = ''.join(result)
    
    # Normalize JSON structure
    for old, new in [
        ("'", '"'),        # Replace single quotes with double quotes
        ('True', 'true'),  # Convert Python booleans to JSON
        ('False', 'false'),
        ('None', 'null')
    ]:
        cleaned = cleaned.replace(old, new)
    
    # Make sure it starts and ends with valid JSON block characters
    if not cleaned.startswith('{'):
        cleaned = '{' + cleaned
    if not cleaned.endswith('}'):
        cleaned = cleaned + '}'
    
    return cleaned

def extract_fallback_world(text: str) -> Dict[str, Any]:
    """
    Extract minimal viable world data using regex patterns when JSON parsing fails
    """
    result = {
        "locations": [],
        "characters": [],
        "items": []
    }
    
    # Pattern to match location objects
    location_pattern = r'"id"\s*:\s*"([^"]+)"[^}]*"name"\s*:\s*"([^"]+)"[^}]*"japanese_name"\s*:\s*"([^"]+)"'
    for match in re.finditer(location_pattern, text):
        loc_id, name, jp_name = match.groups()
        result["locations"].append({
            "id": loc_id,
            "name": name,
            "japanese_name": jp_name,
            "description": "A place in the world.",
            "japanese_description": "世界の場所。",
            "connections": {}
        })
    
    # Pattern to match character objects
    char_pattern = r'"id"\s*:\s*"([^"]+)"[^}]*"name"\s*:\s*"([^"]+)"[^}]*"japanese_name"\s*:\s*"([^"]+)"[^}]*"location"\s*:\s*"([^"]+)"'
    for match in re.finditer(char_pattern, text):
        char_id, name, jp_name, location = match.groups()
        result["characters"].append({
            "id": char_id,
            "name": name,
            "japanese_name": jp_name,
            "description": "A character in the world.",
            "japanese_description": "世界のキャラクター。",
            "location": location,
            "dialogues": {"default": {"response": "Hello.", "japanese_response": "こんにちは。"}}
        })
    
    # Ensure we have at least a start location if nothing was found
    if not result["locations"]:
        result["locations"].append({
            "id": "start",
            "name": "Starting Location",
            "japanese_name": "開始地点",
            "description": "The starting point of your adventure.",
            "japanese_description": "あなたの冒険の出発点。",
            "connections": {}
        })
    
    return result

class LLMService:
    def __init__(self):
        self.llm_host = os.getenv("LLM_HOST", "localhost")
        self.llm_port = os.getenv("LLM_PORT", "9000")
        self.base_url = f"http://{self.llm_host}:{self.llm_port}/v1/chat/completions"
        self.world_model = os.getenv("WORLD_MODEL", "qwen2.5:7b")
        self.game_model = os.getenv("GAME_MODEL", "qwen2.5:14b")
        self.japanese_model = os.getenv("JAPANESE_MODEL", "qwen2.5:14b")
        self.game_engine = GameEngine()
        logger.info(f"LLM Service initialized with base URL: {self.base_url}")
        
    async def _call_llm(self, prompt: str, model: str, system_prompt: Optional[str] = None) -> str:
        """
        Call the LLM with proper streaming response handling
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            
            logger.info(f"Calling LLM model {model} with prompt: {prompt[:100]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"LLM API error: {error_text}")
                        raise Exception(f"LLM API returned status {response.status}: {error_text}")
                    
                    content = ""
                    buffer = ""
                    
                    # Process the streaming response
                    async for chunk in response.content:
                        chunk_str = chunk.decode('utf-8')
                        logger.debug(f"Raw chunk: {chunk_str!r}")
                        
                        # Add to buffer and process complete messages
                        buffer += chunk_str
                        # Process all complete SSE messages in buffer
                        while '\n\n' in buffer:
                            message, buffer = buffer.split('\n\n', 1)
                            # Process each line in the message
                            for line in message.split('\n'):
                                if line.startswith('data: '):
                                    data = line[6:].strip()
                                    if data == "[DONE]":
                                        continue  # Skip [DONE] marker but keep processing
                                    
                                    try:
                                        json_data = json.loads(data)
                                        if 'choices' in json_data and len(json_data['choices']) > 0:
                                            delta = json_data['choices'][0].get('delta', {})
                                            if 'content' in delta and delta['content']:
                                                content += delta['content']
                                                logger.debug(f"Current content: {content[:100]}...")
                                    except json.JSONDecodeError:
                                        logger.warning(f"Failed to parse JSON: {data}")
                                        # Continue processing rather than breaking
                                        continue
            
            logger.info(f"LLM response completed: {content[:100]}...")
            return content
        
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            raise
    
    async def generate_world(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a game world from a user prompt
        """
        system_prompt = """You are a world-building assistant for a Japanese text adventure game.
        Generate a detailed world description in JSON format containing:
        
        {
          "locations": [
            {
              "id": "start",
              "name": "Starting Village",
              "japanese_name": "始まりの村",
              "description": "A small village nestled between mountains...",
              "japanese_description": "山々に囲まれた小さな村...",
              "connections": {
                "north": "forest",
                "east": "river"
              },
              "vocabulary": [
                {"japanese": "村", "english": "village", "reading": "むら"},
                {"japanese": "山", "english": "mountain", "reading": "やま"}
              ]
            }
          ],
          "characters": [
            {
              "id": "elder",
              "name": "Village Elder",
              "japanese_name": "村長",
              "description": "An old wise man with a long white beard...",
              "japanese_description": "長い白いひげを持つ賢い老人...",
              "location": "start",
              "dialogues": {
                "default": {
                  "response": "Welcome, traveler. How may I help you?",
                  "japanese_response": "いらっしゃい、旅人さん。何かお手伝いできることはありますか？"
                },
                "quest": {
                  "response": "We have a problem with the forest spirits...",
                  "japanese_response": "森の精霊に問題があります..."
                }
              },
              "vocabulary": [
                {"japanese": "村長", "english": "village elder", "reading": "そんちょう"},
                {"japanese": "旅人", "english": "traveler", "reading": "たびびと"}
              ]
            }
          ],
          "items": [
            {
              "id": "map",
              "name": "Ancient Map",
              "japanese_name": "古地図",
              "description": "A weathered map showing the surrounding area...",
              "japanese_description": "周辺地域を示す風化した地図...",
              "type": "quest",
              "location": "start",
              "properties": {
                "use_effect": "The map reveals a hidden path to the east."
              },
              "vocabulary": [
                {"japanese": "地図", "english": "map", "reading": "ちず"},
                {"japanese": "古い", "english": "old, ancient", "reading": "ふるい"}
              ]
            }
          ],
          "vocabulary": [
            {
              "japanese": "冒険",
              "english": "adventure",
              "reading": "ぼうけん",
              "part_of_speech": "noun",
              "example_sentence": "新しい冒険が始まります。",
              "notes": "Used to refer to an exciting or dangerous journey."
            }
          ]
        }
        
        The world should be creative, coherent, and suitable for a text adventure game
        that helps users learn Japanese. Include Japanese names and descriptions for all
        elements. Make sure all connections between locations are logical and bidirectional.
        
        Create at least:
        - 5-7 diverse locations with Japanese names and descriptions
        - 3-5 characters with dialogue options in both English and Japanese
        - 5-7 items that can be found and used, with Japanese names
        - 10+ vocabulary entries relevant to the game world
        
        Ensure all Japanese text is grammatically correct and uses appropriate kanji with
        furigana readings where needed. Use simple Japanese suitable for beginners where
        appropriate, and include useful vocabulary in descriptions.
        
        The theme should incorporate elements from Japanese culture and mythology.
        
        Return only the valid JSON object without any explanation or additional text."""
        
        try:
            # Include the user's prompt in our world generation request
            enhanced_prompt = f"""
            Create a Japanese-themed fantasy world based on the following concept:
            
            {prompt}
            
            Include elements of Japanese culture, language learning opportunities, and
            interesting locations to explore. Make the world coherent and interconnected
            with a central theme.
            """
            
            try:
                # Try to call the LLM
                response = await self._call_llm(enhanced_prompt, self.world_model, system_prompt)
                
                # Clean the response
                clean_response = clean_json_string(response)
                
                try:
                    # Log the cleaned string for debugging
                    logger.debug(f"Attempting to parse JSON: {clean_response[:100]}...")
                    
                    try:
                        # Try Python's built-in JSON parser first
                        world_data = json.loads(clean_response)
                    except json.JSONDecodeError as e:
                        # Get specific error information
                        error_position = e.pos
                        error_line, error_col = e.lineno, e.colno
                        
                        # Log the specific part of the JSON that's problematic
                        start = max(0, error_position - 20)
                        end = min(len(clean_response), error_position + 20)
                        context = clean_response[start:end]
                        
                        logger.error(f"JSON error context: ...{context}... (error at position {error_position})")
                        logger.error(f"Character at error position: '{clean_response[error_position:error_position+1]}' (0x{ord(clean_response[error_position]):02x})")
                        
                        # Try more aggressive JSON cleaning
                        logger.info("Attempting extreme JSON cleaning...")
                        extreme_clean = extreme_json_clean(clean_response)
                        try:
                            world_data = json.loads(extreme_clean)
                            logger.info("Extreme JSON cleaning succeeded!")
                        except json.JSONDecodeError:
                            # Try yet another approach - extract just locations, characters, and items
                            logger.warning("Extreme cleaning failed, trying direct extraction...")
                            
                            # Try the direct extract method which builds a minimal JSON structure
                            try:
                                world_data = extract_fallback_world(response)
                                logger.info("Direct extraction succeeded with minimal structure")
                            except Exception as extract_error:
                                logger.error(f"Failed direct extraction: {extract_error}")
                                
                                # Ultimate fallback - force a default world template
                                logger.warning("All extraction methods failed, using default world")
                                world_data = DEFAULT_WORLD
                    
                    # Add template quests to the world data
                    world_data = self.add_template_content(world_data)
                    
                    # Initialize the game state with our game engine
                    game_state = self.game_engine.init_game_state(world_data)
                    
                    # Return the processed world data
                    return world_data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {str(e)}")
                    # Try to extract the JSON part
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        clean_json = clean_json_string(response[json_start:json_end])
                        try:
                            world_data = json.loads(clean_json)
                            
                            # Add template quests to the world data
                            world_data = self.add_template_content(world_data)
                            
                            return world_data
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse extracted JSON: {clean_json[:100]}...")
                    
                    # If we still can't parse JSON, fall back to the default world
                    logger.warning("Using default world template due to parsing failure")
                    return self.add_template_content(DEFAULT_WORLD)
            
            except Exception as e:
                logger.error(f"LLM call failed: {str(e)}")
                # If the LLM call fails, use the default world
                logger.warning("Using default world template due to LLM call failure")
                return self.add_template_content(DEFAULT_WORLD)
            
        except Exception as e:
            logger.error(f"Error generating world: {str(e)}")
            # Final fallback
            return self.add_template_content(DEFAULT_WORLD)
    
    def add_template_content(self, world_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add template quests and hidden locations to the world data
        """
        # Make a copy to avoid modifying the original
        world_data = world_data.copy()
        
        # Initialize quests list if it doesn't exist
        if "quests" not in world_data:
            world_data["quests"] = []
        
        # Add template quests
        world_data["quests"].extend(DEFAULT_QUESTS)
        
        # Add quest items to the items list
        if "items" not in world_data:
            world_data["items"] = []
        
        world_data["items"].extend(QUEST_ITEMS)
        
        # Add hidden locations to the locations list
        if "locations" not in world_data:
            world_data["locations"] = []
        
        world_data["locations"].extend(HIDDEN_LOCATIONS)
        
        # Ensure the starting location has the map quest trigger
        start_location_found = False
        for location in world_data["locations"]:
            if location.get("id") == "start":
                start_location_found = True
                if "quest_triggers" not in location:
                    location["quest_triggers"] = []
                if "quest_village_map" not in location["quest_triggers"]:
                    location["quest_triggers"].append("quest_village_map")
                # Ensure the starting location has at least one connection
                if "connections" not in location or not location["connections"]:
                    location["connections"] = {
                        "north": "forest",
                        "east": "shop",
                        "west": "house",
                        "south": "river"
                    }
        
        # If there's no start location, add it
        if not start_location_found and "locations" in world_data:
            for location in world_data["locations"]:
                if "id" not in location:
                    location["id"] = "start"
                    if "quest_triggers" not in location:
                        location["quest_triggers"] = []
                    if "quest_village_map" not in location["quest_triggers"]:
                        location["quest_triggers"].append("quest_village_map")
                    # Ensure the starting location has connections
                    if "connections" not in location or not location["connections"]:
                        location["connections"] = {
                            "north": "forest",
                            "east": "shop",
                            "west": "house",
                            "south": "river"
                        }
                    break
            
        # If we still don't have a start location, create one with connections
        if not start_location_found:
            start_location = {
                "id": "start",
                "name": "Village Square",
                "japanese_name": "村の広場",
                "description": "A peaceful village square where your adventure begins. Cherry blossom trees line the edges, and a small fountain stands in the center.",
                "japanese_description": "あなたの冒険が始まる平和な村の広場です。桜の木が周りに並び、中央に小さな噴水があります。",
                "connections": {
                    "north": "forest",
                    "east": "shop",
                    "west": "house",
                    "south": "river"
                },
                "quest_triggers": ["quest_village_map"]
            }
            world_data["locations"].append(start_location)
        
        # Ensure all the connected locations from start location exist
        if "locations" in world_data:
            start_location = next((loc for loc in world_data["locations"] if loc.get("id") == "start"), None)
            if start_location and "connections" in start_location:
                for direction, target_id in start_location["connections"].items():
                    # Check if the target location exists
                    target_exists = any(loc.get("id") == target_id for loc in world_data["locations"])
                    if not target_exists:
                        # Create the missing location
                        new_location = {
                            "id": target_id,
                            "name": target_id.capitalize() + " Area",
                            "japanese_name": target_id.capitalize() + "エリア",
                            "description": f"A {target_id} area connected to the village square.",
                            "japanese_description": f"村の広場につながる{target_id}エリアです。",
                            "connections": {
                                # Add reverse connection to start
                                self.game_engine.get_opposite_direction(direction): "start"
                            }
                        }
                        world_data["locations"].append(new_location)
        
        # Ensure "elder" character has quest dialogue for the village wisdom quest
        elder_found = False
        if "characters" in world_data:
            for character in world_data["characters"]:
                if character.get("id") == "elder":
                    elder_found = True
                    if "quest_ids" not in character:
                        character["quest_ids"] = []
                    if "quest_talk_to_elder" not in character["quest_ids"]:
                        character["quest_ids"].append("quest_talk_to_elder")
                    
                    # Add quest dialogue
                    if "quest_dialogues" not in character:
                        character["quest_dialogues"] = {}
                    if "quest_talk_to_elder" not in character["quest_dialogues"]:
                        character["quest_dialogues"]["quest_talk_to_elder"] = {
                            "in_progress": {
                                "response": "Ah, you wish to learn about our village's history? There is an old path through the forest that few know about. It leads to sacred grounds deep in the mountains.",
                                "japanese_response": "ああ、村の歴史について学びたいですか？森を通る古い道があり、それを知る人はほとんどいません。山の奥にある神聖な場所へ続いています。"
                            },
                            "completed": {
                                "response": "Remember to tread carefully on your journey. The mountains hold many secrets.",
                                "japanese_response": "旅の途中で気をつけてください。山には多くの秘密があります。"
                            }
                        }
        
        # Similarly ensure other NPCs have appropriate quest dialogues
        if "characters" in world_data:
            for character in world_data["characters"]:
                if character.get("id") == "priest":
                    if "quest_ids" not in character:
                        character["quest_ids"] = []
                    if "quest_shrine_offering" not in character["quest_ids"]:
                        character["quest_ids"].append("quest_shrine_offering")
                    
                    # Add quest dialogue
                    if "quest_dialogues" not in character:
                        character["quest_dialogues"] = {}
                    if "quest_shrine_offering" not in character["quest_dialogues"]:
                        character["quest_dialogues"]["quest_shrine_offering"] = {
                            "in_progress": {
                                "response": "Have you brought an offering for the shrine? Traditional offerings include rice, sake, or fresh fruits.",
                                "japanese_response": "神社へのお供えを持ってきましたか？伝統的なお供えには、お米、お酒、新鮮な果物などがあります。"
                            },
                            "completed": {
                                "response": "Thank you for your offering. Please accept this protective charm as a token of the shrine's blessing.",
                                "japanese_response": "お供えをありがとうございます。神社の祝福の印として、このお守りをお受け取りください。"
                            }
                        }
        
        return world_data
    
    async def process_game_input(
        self, 
        user_input: str, 
        game_state_dict: Dict[str, Any], 
        chat_history: List[Dict[str, str]]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process user input for the game
        """
        try:
            # Check if we have a properly initialized GameState
            if "world" not in game_state_dict or "player" not in game_state_dict:
                logger.warning("Game state not properly initialized, attempting to rebuild")
                # Try to convert the dictionary to our GameState model
                game_state = self.game_engine.init_game_state(game_state_dict.get("world", {}))
                game_state.player.current_location = game_state_dict.get("current_location", "start")
                game_state.player.inventory = game_state_dict.get("inventory", [])
            else:
                # We have a proper state, use it directly
                # Note: This is a simplification and should be replaced with proper parsing
                game_state = GameState(
                    world=game_state_dict["world"],
                    player=game_state_dict["player"],
                    visited_locations=set(game_state_dict.get("visited_locations", [])),
                    flags=game_state_dict.get("flags", {}),
                    metadata=game_state_dict.get("metadata", {}),
                    quest_log=game_state_dict.get("quest_log", {})
                )
            
            # First try to process the command with our game engine
            response, updated_game_state = self.game_engine.process_command(user_input, game_state)
            
            # If the command wasn't recognized or needs more context, use the LLM to enhance the response
            if "I don't understand" in response:
                # Let the LLM try to interpret the command
                system_prompt = """You are a Japanese text adventure game assistant.
                The player has entered a command that wasn't recognized by the standard
                parser. Try to interpret what they meant and provide a helpful response
                that stays in character for the game world. Include some Japanese phrases
                where appropriate to enhance language learning."""
                
                # Prepare the prompt with game context
                current_loc_id = game_state.player.current_location
                current_loc = game_state.world.locations.get(current_loc_id)
                context = f"""
                The player is currently at: {current_loc.name} ({current_loc.japanese_name})
                
                Location description: {current_loc.description}
                
                Characters present: {[game_state.world.characters.get(c).name for c in current_loc.characters if game_state.world.characters.get(c)]}
                
                Items visible: {[game_state.world.items.get(i).name for i in current_loc.items if game_state.world.items.get(i) and not game_state.world.items.get(i).hidden]}
                
                The player typed: "{user_input}"
                
                Interpret what they might have meant and provide a helpful response
                that teaches them how to play while staying in character for the game.
                Include at least one relevant Japanese phrase with its English translation.
                """
                
                try:
                    llm_response = await self._call_llm(context, self.game_model, system_prompt)
                    # Combine the responses
                    response = f"Command not recognized. {llm_response}"
                except Exception as e:
                    logger.error(f"Failed to get LLM interpretation: {str(e)}")
                    # Fallback to a generic response with some Japanese
                    response = "そのコマンドは分かりません (I don't understand that command). Try simple commands like 'look', 'north', or 'take map'."
            
            # Enhance the response with Japanese vocabulary where appropriate
            elif "Look" in response or "You see" in response or "Inventory" in response:
                # Let's add some vocabulary hints for key words
                system_prompt = """You are a Japanese language assistant. 
                Identify 1-3 important words in the given text that would be useful vocabulary
                for a Japanese language learner. Provide the Japanese translation, 
                reading, and a brief note for each. Format your response like this:
                
                [New Words]
                - word: 「日本語」 (にほんご) - a brief note about usage
                """
                
                try:
                    vocab_response = await self._call_llm(response, self.japanese_model, system_prompt)
                    
                    # Add vocabulary to the response if we got some
                    if "[New Words]" in vocab_response:
                        response = f"{response}\n\n{vocab_response}"
                except Exception as e:
                    logger.error(f"Failed to get vocabulary hints: {str(e)}")
                    # Just continue without vocabulary hints
            
            # Convert the updated game state back to a dictionary
            game_state_dict = updated_game_state.dict()
            
            return response, game_state_dict
            
        except Exception as e:
            logger.error(f"Error processing game input: {str(e)}")
            return "申し訳ありません (I'm sorry), there was an error processing your command. Please try again.", game_state_dict
    
    async def validate_japanese(self, text: str) -> Tuple[bool, str]:
        """
        Validate if the Japanese text input is grammatically correct
        """
        system_prompt = """You are a Japanese language validator.
        You are helping users learn Japanese through a text adventure game.
        Analyze the given text and determine if it is grammatically correct Japanese.
        If it contains no Japanese characters or is just a romanized version, explain
        how to type actual Japanese characters.
        If it's incorrect Japanese, provide helpful feedback on how to correct it.
        If it's correct, provide positive reinforcement and maybe add a small tidbit
        about the grammar or vocabulary used.
        
        Be encouraging and helpful, as the user is trying to learn Japanese."""
        
        prompt = f"""Please validate this text:
        
        {text}
        
        Is this grammatically correct Japanese? If not, what corrections are needed?
        If it contains no Japanese characters, explain how the user might type actual
        Japanese characters instead of romaji.
        
        Respond in this format:
        VALID: true/false
        FEEDBACK: your feedback here"""
        
        try:
            try:
                response = await self._call_llm(prompt, self.japanese_model, system_prompt)
                
                # Parse the response
                is_valid = "VALID: true" in response.upper()
                
                # Extract feedback
                feedback_start = response.upper().find("FEEDBACK:")
                feedback = ""
                if feedback_start >= 0:
                    feedback = response[feedback_start + 9:].strip()
                else:
                    feedback = response  # If format not followed, use the whole response
                
                return is_valid, feedback
            except Exception as e:
                logger.error(f"LLM validation failed: {str(e)}")
                # Provide a fallback validation if the LLM call fails
                has_japanese = bool(re.search(r'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]', text))
                if has_japanese:
                    return True, "Your Japanese looks good! (Note: Validation is currently limited due to technical issues)"
                else:
                    return False, "Text doesn't appear to contain Japanese characters. Try using a Japanese keyboard input method to type in Japanese."
        except Exception as e:
            logger.error(f"Error validating Japanese: {str(e)}")
            return True, "Validation is temporarily unavailable, but please continue practicing your Japanese!" 