from typing import Dict, List, Tuple, Any, Optional, Set
import re
from app.models.game import (
    GameState, World, Player, Location, Item, Character,
    Direction, ItemType, VocabularyEntry, LearnedVocabulary
)
from app.services.quest_handler import QuestHandler
from datetime import datetime
from loguru import logger


class GameEngine:
    def __init__(self):
        self.direction_synonyms = {
            "n": Direction.NORTH,
            "s": Direction.SOUTH,
            "e": Direction.EAST,
            "w": Direction.WEST,
            "u": Direction.UP,
            "d": Direction.DOWN,
            "north": Direction.NORTH,
            "south": Direction.SOUTH,
            "east": Direction.EAST,
            "west": Direction.WEST,
            "up": Direction.UP,
            "down": Direction.DOWN,
            "inside": Direction.IN,
            "outside": Direction.OUT,
            "enter": Direction.IN,
            "exit": Direction.OUT,
        }
        
        # Action commands and their synonyms
        self.action_commands = {
            "look": ["look", "examine", "inspect", "check", "見る", "調べる"],
            "take": ["take", "get", "grab", "pick", "持つ", "取る", "拾う"],
            "drop": ["drop", "leave", "put", "置く", "捨てる"],
            "inventory": ["inventory", "items", "belongings", "i", "持ち物", "インベントリー"],
            "use": ["use", "activate", "apply", "使う", "使用する"],
            "talk": ["talk", "speak", "chat", "converse", "ask", "話す", "聞く", "質問"],
            "help": ["help", "commands", "助け", "ヘルプ", "コマンド"],
            "quests": ["quests", "quest", "missions", "tasks", "クエスト", "任務"],
            "grammar": ["grammar", "practice", "文法", "練習"]
        }
        
        self.quest_handler = QuestHandler()
    
    def create_fallback_location(self, location_id: str, game_state: GameState) -> Location:
        """Create a fallback location when the specified location ID is missing"""
        logger.warning(f"Creating fallback location for missing ID: {location_id}")
        
        # Create default names based on ID
        name = f"Area {location_id}"
        japanese_name = f"エリア {location_id}"
        
        if location_id == "start":
            name = "Starting Point"
            japanese_name = "開始地点"
            description = "You find yourself at the starting point of your adventure."
            japanese_description = "あなたは冒険の出発点にいます。"
        else:
            description = f"A mysterious area that seems to have appeared out of nowhere."
            japanese_description = f"どこからともなく現れた不思議なエリア。"
        
        # Create a basic fallback location
        fallback_location = Location(
            id=location_id,
            name=name,
            japanese_name=japanese_name,
            description=description,
            japanese_description=japanese_description,
            connections={},
            characters=[],
            items=[],
            vocabulary=[],
            visited=False
        )
        
        # Add it to the world
        game_state.world.locations[location_id] = fallback_location
        logger.info(f"Added fallback location '{name}' to world")
        
        return fallback_location
    
    def ensure_valid_location(self, location_id: str, game_state: GameState) -> Location:
        """Ensure a valid location exists for the given ID, creating a fallback if needed"""
        location = game_state.world.locations.get(location_id)
        
        if not location:
            # Create a fallback location if it doesn't exist
            location = self.create_fallback_location(location_id, game_state)
            
            # If this is the player's current location, make sure it's flagged as visited
            if game_state.player.current_location == location_id:
                location.visited = True
                game_state.visited_locations.add(location_id)
        
        return location
    
    def validate_world_structure(self, world: World) -> World:
        """
        Validate and fix the world structure, ensuring connections are bidirectional,
        all referenced locations exist (creating placeholders if needed), and basic
        integrity checks pass.

        Args:
            world: The world object to validate and fix

        Returns:
            The validated and fixed world object
        """
        logger.info("Validating world structure...")
        fixed_issues = 0
        all_location_ids = set(world.locations.keys())
        referenced_location_ids = set()

        # --- Step 1: Collect all referenced location IDs and basic validation ---
        locations_to_process = list(world.locations.items()) # Create a copy for safe iteration
        for loc_id, location in locations_to_process:
            if not location: # Skip if somehow None
                 logger.warning(f"Found None location object for ID: {loc_id}. Removing.")
                 del world.locations[loc_id]
                 all_location_ids.remove(loc_id)
                 fixed_issues += 1
                 continue

            # Basic check: Ensure location has an ID matching its key
            if not hasattr(location, 'id') or location.id != loc_id:
                logger.warning(f"Location key '{loc_id}' mismatch or missing ID attribute. Fixing.")
                location.id = loc_id
                fixed_issues += 1

            # Basic check: Ensure essential attributes exist (using defaults if not)
            if not hasattr(location, 'name') or not location.name:
                 location.name = f"Unnamed Area ({loc_id})"
                 logger.warning(f"Location '{loc_id}' has missing/empty name. Setting default.")
                 fixed_issues += 1
            if not hasattr(location, 'description'):
                 location.description = "An undefined area."
                 logger.warning(f"Location '{loc_id}' has missing description. Setting default.")
                 fixed_issues += 1
            if not hasattr(location, 'connections'):
                 location.connections = {}
                 logger.warning(f"Location '{loc_id}' has missing connections attribute. Initializing.")
                 fixed_issues += 1
            if not hasattr(location, 'items'): location.items = []
            if not hasattr(location, 'characters'): location.characters = []
            if not hasattr(location, 'hidden'): location.hidden = False

            # Collect referenced IDs from connections
            connection_ids = set(location.connections.values())
            referenced_location_ids.update(connection_ids)

        # --- Step 2: Identify and create placeholders for missing referenced locations ---
        missing_location_ids = referenced_location_ids - all_location_ids
        if missing_location_ids:
            logger.warning(f"Found references to non-existent locations: {missing_location_ids}. Creating placeholders.")
            for missing_id in missing_location_ids:
                placeholder_loc = Location(
                    id=missing_id,
                    name=f"Unknown Area ({missing_id})",
                    japanese_name=f"不明なエリア ({missing_id})",
                    description="This area seems incomplete or lost to time.",
                    japanese_description="不完全か、時の流れに失われたようなエリアです。",
                    connections={},
                    items=[],
                    characters=[],
                    vocabulary=[],
                    visited=False,
                    hidden=False # Make placeholders visible initially for debugging
                )
                world.locations[missing_id] = placeholder_loc
                all_location_ids.add(missing_id) # Add to our set of known IDs
                fixed_issues += 1
            logger.info(f"Created {len(missing_location_ids)} placeholder locations.")

        # --- Step 3: Verify and fix bidirectional connections for ALL locations ---
        logger.info("Verifying and fixing bidirectional connections...")
        locations_to_process = list(world.locations.items()) # Re-list including placeholders
        for loc_id, location in locations_to_process:
             # Ensure connections dict exists
             if not hasattr(location, 'connections'): location.connections = {}

             connections_to_remove = [] # Store invalid connections to remove later
             for direction, target_id in list(location.connections.items()): # Iterate over copy for safe modification
                 # Check if the target location now exists (it should after step 2)
                 target_location = world.locations.get(target_id)
                 if not target_location:
                     # This shouldn't happen if step 2 worked, but handle defensively
                     logger.error(f"Connection validation inconsistency: Target ID '{target_id}' from '{loc_id}' not found even after placeholder creation. Removing connection.")
                     connections_to_remove.append(direction)
                     fixed_issues += 1
                     continue

                 # Check/fix the reverse connection
                 opposite_direction = self.get_opposite_direction(direction)
                 if opposite_direction is None:
                      logger.warning(f"Could not determine opposite direction for {direction} from {loc_id}. Skipping reverse check.")
                      continue

                 if not hasattr(target_location, 'connections'): target_location.connections = {}

                 # Check if opposite connection exists
                 if opposite_direction not in target_location.connections:
                     logger.warning(f"Missing reverse connection from '{target_id}' ({opposite_direction}) back to '{loc_id}'. Adding.")
                     logger.debug(f"--> ADDING connection: {target_id}.connections[{opposite_direction}] = {loc_id}")
                     target_location.connections[opposite_direction] = loc_id
                     fixed_issues += 1
                 # Check if it points correctly
                 elif target_location.connections[opposite_direction] != loc_id:
                     logger.warning(f"Incorrect reverse connection from '{target_id}' ({opposite_direction}). Expected '{loc_id}', found '{target_location.connections[opposite_direction]}'. Fixing.")
                     logger.debug(f"--> FIXING connection: {target_id}.connections[{opposite_direction}] = {loc_id}")
                     target_location.connections[opposite_direction] = loc_id
                     fixed_issues += 1

             # Remove connections marked for removal
             for direction in connections_to_remove:
                 del location.connections[direction]


        # --- Step 4: Ensure 'start' location exists and has connections ---
        if "start" not in world.locations:
            logger.warning("No 'start' location found. Creating a default start location.")
            start_location = Location(
                id="start", name="Starting Point", japanese_name="開始地点",
                description="The beginning of your adventure.", japanese_description="冒険の始まり。",
                connections={}, items=[], characters=[], vocabulary=[], visited=False, hidden=False
            )
            world.locations["start"] = start_location
            fixed_issues += 1
            all_location_ids.add("start")

        start_location = world.locations["start"]
        if not start_location.connections:
            logger.warning("'start' location has no connections. Attempting to add default connections.")
            default_connections = { "north": "forest", "east": "shop", "west": "house", "south": "river" }
            added_connection = False
            for direction, target_id in default_connections.items():
                 # Check if target exists or create placeholder if needed
                 if target_id not in world.locations:
                      logger.warning(f"Default connection target '{target_id}' for start location does not exist. Creating placeholder.")
                      placeholder_loc = Location(id=target_id, name=target_id.capitalize(), description=f"The {target_id} area.", connections={}, items=[], characters=[], vocabulary=[], visited=False, hidden=False)
                      world.locations[target_id] = placeholder_loc
                      all_location_ids.add(target_id)
                      fixed_issues += 1

                 target_location = world.locations[target_id]
                 start_location.connections[direction] = target_id
                 opposite_direction = self.get_opposite_direction(direction)
                 if opposite_direction:
                    if not hasattr(target_location, 'connections'): target_location.connections = {}
                    if opposite_direction not in target_location.connections:
                        target_location.connections[opposite_direction] = "start"
                 added_connection = True
                 logger.info(f"Added default connection: start --{direction}--> {target_id}")

            if not added_connection and len(world.locations) > 1:
                 # If still no connections, connect to the first other location found
                 first_other_id = next((lid for lid in all_location_ids if lid != "start"), None)
                 if first_other_id:
                     logger.warning(f"Connecting 'start' location to the first available location: '{first_other_id}'.")
                     start_location.connections["north"] = first_other_id # Default to north
                     opposite = self.get_opposite_direction("north")
                     if opposite:
                        if not hasattr(world.locations[first_other_id], 'connections'): world.locations[first_other_id].connections = {}
                        world.locations[first_other_id].connections[opposite] = "start"
                     fixed_issues += 1

        # --- Step 5: Validate Character/Item placements (Optional but Recommended) ---
        # (Keep existing validation logic for character/item locations if desired)
        logger.info("Validating character and item placements...")
        all_item_ids = set(world.items.keys())
        all_character_ids = set(world.characters.keys())

        locations_to_process = list(world.locations.values()) # Use values for iteration
        for location in locations_to_process:
            # Validate items in location
            items_to_remove = []
            if hasattr(location, 'items'):
                for item_id in location.items:
                    if item_id not in all_item_ids:
                        logger.warning(f"Location '{location.id}' contains non-existent item ID '{item_id}'. Removing reference.")
                        items_to_remove.append(item_id)
                        fixed_issues += 1
                # Remove invalid items safely
                location.items = [item for item in location.items if item not in items_to_remove]
            else:
                location.items = [] # Ensure attribute exists

            # Validate characters in location
            chars_to_remove = []
            if hasattr(location, 'characters'):
                for char_id in location.characters:
                    if char_id not in all_character_ids:
                        logger.warning(f"Location '{location.id}' contains non-existent character ID '{char_id}'. Removing reference.")
                        chars_to_remove.append(char_id)
                        fixed_issues += 1
                # Remove invalid characters safely
                location.characters = [char for char in location.characters if char not in chars_to_remove]
            else:
                 location.characters = [] # Ensure attribute exists

        # --- Step 6: Final Safety Net - Connect Orphaned Locations to Start ---
        logger.info("Checking for orphaned locations...")
        locations_to_process = list(world.locations.values())
        for location in locations_to_process:
            # Ensure connections dict exists
            if not hasattr(location, 'connections'): location.connections = {}
            
            # If a location isn't 'start' and has no connections after all validation
            if location.id != "start" and not location.connections:
                logger.warning(f"Location '{location.id}' is orphaned (no connections). Connecting to 'start'.")
                # Add connection from orphan to start
                location.connections["south"] = "start" # Default connection direction
                fixed_issues += 1
                
                # Add connection from start back to orphan
                start_location = world.locations.get("start")
                if start_location:
                    opposite_direction = self.get_opposite_direction("south") # Should be 'north'
                    if opposite_direction:
                         if not hasattr(start_location, 'connections'): start_location.connections = {}
                         # Avoid overwriting existing connection from start if possible, maybe choose another direction?
                         # For simplicity now, we might overwrite. A better approach could find an unused direction.
                         start_location.connections[opposite_direction] = location.id
                         logger.info(f"Added reverse connection from 'start' ({opposite_direction}) to '{location.id}'.")
                    else:
                        logger.error(f"Could not determine opposite direction for forced connection from {location.id}")
                else:
                     logger.error("Cannot add reverse connection for orphaned location '{location.id}' because 'start' location is missing.")


        logger.info(f"World structure validation completed. Issues fixed: {fixed_issues}")
        return world
    
    def init_game_state(self, world_data: Dict[str, Any]) -> GameState:
        """Initialize a new game state from world data"""
        # Convert the LLM-generated world data into our structured format
        world = World()
        
        # Process locations
        for loc_data in world_data.get("locations", []):
            loc_id = loc_data.get("id", f"loc_{len(world.locations)}")
            location = Location(
                id=loc_id,
                name=loc_data.get("name", "Unknown Location"),
                japanese_name=loc_data.get("japanese_name", ""),
                description=loc_data.get("description", ""),
                japanese_description=loc_data.get("japanese_description", ""),
                connections={},
                characters=[],
                items=[],
                vocabulary=loc_data.get("vocabulary", []),
                visited=False,
                quest_triggers=loc_data.get("quest_triggers", []),
                hidden=loc_data.get("hidden", False)
            )
            
            # Process connections
            for direction, target in loc_data.get("connections", {}).items():
                if isinstance(target, str):
                    location.connections[direction] = target
                else:
                    # If it's a more complex connection object
                    target_id = target.get("location") if isinstance(target, dict) else str(target)
                    location.connections[direction] = target_id
            
            world.locations[loc_id] = location
        
        # Ensure we have a start location
        if "start" not in world.locations:
            logger.warning("No start location found in world data, creating default start location")
            world.locations["start"] = Location(
                id="start",
                name="Starting Point",
                japanese_name="開始地点",
                description="You find yourself at the starting point of your adventure.",
                japanese_description="あなたは冒険の出発点にいます。",
                connections={},
                characters=[],
                items=[],
                vocabulary=[],
                visited=False
            )
        
        # Process characters
        for char_data in world_data.get("characters", []):
            char_id = char_data.get("id", f"char_{len(world.characters)}")
            character = Character(
                id=char_id,
                name=char_data.get("name", "Unknown Character"),
                japanese_name=char_data.get("japanese_name", ""),
                description=char_data.get("description", ""),
                japanese_description=char_data.get("japanese_description", ""),
                dialogues=char_data.get("dialogues", {}),
                vocabulary=char_data.get("vocabulary", []),
                items=char_data.get("items", []),
                quest_ids=char_data.get("quest_ids", []),
                quest_dialogues=char_data.get("quest_dialogues", {})
            )
            
            # Assign character to its location
            location_id = char_data.get("location", "start")
            if location_id in world.locations:
                world.locations[location_id].characters.append(char_id)
            
            # DO NOT set character.location directly as it's not in the Character model
            # Instead, character locations are tracked through their presence in location.characters lists
            
            world.characters[char_id] = character
        
        # Process items
        for item_data in world_data.get("items", []):
            item_id = item_data.get("id", f"item_{len(world.items)}")
            item = Item(
                id=item_id,
                name=item_data.get("name", "Unknown Item"),
                japanese_name=item_data.get("japanese_name", ""),
                description=item_data.get("description", ""),
                japanese_description=item_data.get("japanese_description", ""),
                item_type=item_data.get("type", ItemType.GENERAL),
                properties=item_data.get("properties", {}),
                vocabulary=item_data.get("vocabulary", []),
                can_be_taken=item_data.get("can_be_taken", True),
                hidden=item_data.get("hidden", False),
                related_quest_id=item_data.get("related_quest_id")
            )
            
            # Assign item to its location
            location_id = item_data.get("location", "start")
            if location_id in world.locations:
                world.locations[location_id].items.append(item_id)
            
            world.items[item_id] = item
        
        # Process vocabulary
        for vocab_data in world_data.get("vocabulary", []):
            vocab_id = vocab_data.get("id", f"vocab_{len(world.vocabulary)}")
            vocab = VocabularyEntry(
                japanese=vocab_data.get("japanese", ""),
                english=vocab_data.get("english", ""),
                reading=vocab_data.get("reading", ""),
                part_of_speech=vocab_data.get("part_of_speech", ""),
                example_sentence=vocab_data.get("example_sentence", ""),
                notes=vocab_data.get("notes", ""),
                jlpt_level=vocab_data.get("jlpt_level")
            )
            world.vocabulary[vocab_id] = vocab
        
        # Process quests
        try:
            for quest_data in world_data.get("quests", []):
                from app.models.quest import Quest, QuestObjective, QuestReward, QuestState
                quest_id = quest_data.get("id", f"quest_{len(world.quests)}")
                
                # Process objectives
                objectives = []
                for obj_data in quest_data.get("objectives", []):
                    from app.models.quest import ObjectiveType
                    objective = QuestObjective(
                        id=obj_data.get("id", f"obj_{len(objectives)}"),
                        type=obj_data.get("type", ObjectiveType.CUSTOM),
                        description=obj_data.get("description", ""),
                        japanese_description=obj_data.get("japanese_description", ""),
                        target_id=obj_data.get("target_id", ""),
                        count=obj_data.get("count", 1),
                        vocabulary=obj_data.get("vocabulary", [])
                    )
                    objectives.append(objective)
                
                # Process rewards
                rewards = []
                for reward_data in quest_data.get("rewards", []):
                    from app.models.quest import RewardType
                    reward = QuestReward(
                        type=reward_data.get("type", RewardType.CUSTOM),
                        description=reward_data.get("description", ""),
                        japanese_description=reward_data.get("japanese_description", ""),
                        target_id=reward_data.get("target_id"),
                        quantity=reward_data.get("quantity", 1),
                        vocabulary=reward_data.get("vocabulary", [])
                    )
                    rewards.append(reward)
                
                quest = Quest(
                    id=quest_id,
                    title=quest_data.get("title", "Untitled Quest"),
                    japanese_title=quest_data.get("japanese_title", ""),
                    description=quest_data.get("description", ""),
                    japanese_description=quest_data.get("japanese_description", ""),
                    objectives=objectives,
                    rewards=rewards,
                    prerequisite_quests=quest_data.get("prerequisite_quests", []),
                    start_location=quest_data.get("start_location"),
                    completion_location=quest_data.get("completion_location"),
                    start_dialogue=quest_data.get("start_dialogue"),
                    completion_dialogue=quest_data.get("completion_dialogue"),
                    difficulty=quest_data.get("difficulty", 1),
                    jlpt_level=quest_data.get("jlpt_level"),
                    hidden=quest_data.get("hidden", False)
                )
                
                world.quests[quest_id] = quest
        except Exception as e:
            logger.warning(f"Error processing quest data: {str(e)}")
            # Continue with initialization even if quests fail to load
        
        # Validate and fix the world structure
        world = self.validate_world_structure(world)
        
        # Create player state
        player = Player(
            current_location="start",
            inventory=[],
            learned_vocabulary={},
            quest_progress={},
            jlpt_level=5,
            last_command_time=datetime.now().isoformat()
        )
        
        # Return the complete game state
        return GameState(
            world=world,
            player=player,
            visited_locations=set(),
            flags={},
            metadata={"version": "0.1.0", "creation_time": datetime.now().isoformat()}
        )
    
    def get_opposite_direction(self, direction: str) -> str:
        """Get the opposite direction for creating bidirectional connections"""
        opposites = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.IN: Direction.OUT,
            Direction.OUT: Direction.IN,
        }
        return opposites.get(direction, Direction.SOUTH)  # Default to SOUTH if unknown
    
    def process_command(self, command: str, game_state: GameState) -> Tuple[str, GameState]:
        """Process a player command and update the game state"""
        if not command:
            return "What would you like to do?", game_state
        
        # Normalize command
        command = command.lower().strip()
        
        # Update stats
        if hasattr(game_state.player, 'stats'):
            game_state.player.stats.moves += 1
        
        # Store last command info
        game_state.player.last_command = command
        game_state.player.last_command_time = datetime.now().isoformat()
        
        # Check for direction movement
        for direction_word, direction in self.direction_synonyms.items():
            if command.startswith(direction_word):
                return self.move_player(direction, game_state)
        
        # Check for action commands
        first_word = command.split()[0]
        for action, synonyms in self.action_commands.items():
            if first_word in synonyms:
                # Extract the object of the command (if any)
                command_object = command[len(first_word):].strip()
                
                # Call the appropriate method based on the action
                if action == "look":
                    return self.look_command(game_state, command_object)
                elif action == "take":
                    return self.take_command(command_object, game_state)
                elif action == "drop":
                    return self.drop_command(command_object, game_state)
                elif action == "inventory":
                    return self.inventory_command(game_state)
                elif action == "use":
                    return self.use_command(command_object, game_state)
                elif action == "talk":
                    return self.talk_command(command_object, game_state)
                elif action == "help":
                    return self.help_command(game_state)
                elif action == "quests":
                    return self.quest_command(command_object, game_state)
                elif action == "grammar":
                    return self.grammar_challenge_command(command_object, game_state)
        
        # Check if this is an answer to a grammar challenge
        if hasattr(game_state, 'active_grammar_challenge') and game_state.active_grammar_challenge:
            try:
                return self.process_grammar_answer(command, game_state)
            except Exception as e:
                logger.error(f"Error processing grammar answer: {str(e)}")
                return "Error processing your answer. Let's continue with our adventure.", game_state
        
        # If we got here, it's an unknown command
        return f"I don't understand '{command}'. Type 'help' for a list of commands.", game_state
    
    def move_player(self, direction: Direction, game_state: GameState) -> Tuple[str, GameState]:
        """Move the player in the specified direction"""
        current_loc_id = game_state.player.current_location
        current_loc = self.ensure_valid_location(current_loc_id, game_state)
        
        # Check if the direction is valid
        if direction not in current_loc.connections:
            return f"You can't go {direction} from here.", game_state
        
        # Get the target location
        target_loc_id = current_loc.connections[direction]
        target_loc = self.ensure_valid_location(target_loc_id, game_state)
        
        # Check if the location is hidden
        if target_loc.hidden:
            return f"That path seems to be blocked. You can't go {direction} from here.", game_state
        
        # Check if the location requires a key
        if hasattr(target_loc, 'requires_key') and target_loc.requires_key:
            key_id = target_loc.requires_key
            if key_id not in game_state.player.inventory:
                key_name = game_state.world.items.get(key_id, Item(id=key_id, name="a key", description="")).name
                return f"You need {key_name} to enter this area.", game_state
        
        # Move the player
        game_state.player.current_location = target_loc_id
        
        # Mark as visited
        if not target_loc.visited:
            target_loc.visited = True
            game_state.visited_locations.add(target_loc_id)
            
            # Update player stats
            if hasattr(game_state.player, 'stats') and hasattr(game_state.player.stats, "locations_visited"):
                if isinstance(game_state.player.stats.locations_visited, list):
                    if target_loc_id not in game_state.player.stats.locations_visited:
                        game_state.player.stats.locations_visited.append(target_loc_id)
                else:
                    game_state.player.stats.locations_visited.add(target_loc_id)
            
            # Check for quest triggers when visiting a new location
            try:
                quest_messages, game_state = self.quest_handler.check_quest_triggers(
                    game_state, "visit_location", target_loc_id
                )
            except Exception as e:
                logger.error(f"Error checking quest triggers: {str(e)}")
                quest_messages = []
            
            # Update quest progress
            try:
                progress_messages, game_state = self.quest_handler.update_quest_progress(
                    game_state, "visit_location", target_loc_id
                )
            except Exception as e:
                logger.error(f"Error updating quest progress: {str(e)}")
                progress_messages = []
        
        # Get the location description
        location_description = self.get_location_description(game_state)
        
        # Combine any quest-related messages with the location description
        if locals().get('quest_messages') and quest_messages:
            location_description += "\n\n" + "\n".join(quest_messages)
        if locals().get('progress_messages') and progress_messages:
            location_description += "\n\n" + "\n".join(progress_messages)
        
        return location_description, game_state
    
    def get_location_description(self, game_state: GameState) -> str:
        """Generate a description of the player's current location, including items and characters."""
        player = game_state.player
        world = game_state.world
        location = world.locations.get(player.current_location)

        if not location:
            logger.error(f"Player location ID '{player.current_location}' not found in world locations.")
            return "You are lost in a void. Something is terribly wrong."

        description_parts = []
        # Location Name and Description
        description_parts.append(f"You are in {location.name}" + (f" ({location.japanese_name})" if location.japanese_name else "") + ".")
        description_parts.append(location.description)
        if location.japanese_description:
            description_parts.append(f"({location.japanese_description})")

        # Format Exits
        exits = []
        for direction, target_id in location.connections.items():
            target_loc = world.locations.get(target_id)
            # Only show exits to non-hidden locations or locations that exist
            if target_loc and not target_loc.hidden:
                 # Show target location name if available, otherwise ID
                 target_name = target_loc.name if target_loc.name else target_id
                 exits.append(f"{direction.capitalize()} ({target_name})")
            elif not target_loc:
                logger.warning(f"Location '{location.id}' connects to non-existent location '{target_id}' via {direction}.")

        if exits:
            description_parts.append(f"Exits: {', '.join(exits)}.")
        else:
            description_parts.append("There are no obvious exits.")

        logger.debug(f"Location {location.id} items: {getattr(location, 'items', '[Attribute missing]')}") # Log items
        # Format Visible Items
        visible_items_str_list = []
        if hasattr(location, 'items') and location.items: # Check if items attribute exists and is not empty
            for item_id in location.items:
                item = world.items.get(item_id)
                if item and not item.hidden:
                    item_name = f"{item.name}" + (f" ({item.japanese_name})" if item.japanese_name else "")
                    visible_items_str_list.append(item_name)
                elif not item:
                     logger.warning(f"Item ID '{item_id}' listed in location '{location.id}' not found in world items.")

        if visible_items_str_list:
            description_parts.append(f"You see: {', '.join(visible_items_str_list)}.")
        # Optional: Add 'You see nothing special.' if list is empty? Decide based on desired verbosity.

        logger.debug(f"Location {location.id} characters: {getattr(location, 'characters', '[Attribute missing]')}") # Log characters
        # Format Present Characters
        present_characters_str_list = []
        if hasattr(location, 'characters') and location.characters: # Check if characters attribute exists and is not empty
            for char_id in location.characters:
                character = world.characters.get(char_id)
                # Assuming characters don't have a 'hidden' flag for now
                if character:
                    char_name = f"{character.name}" + (f" ({character.japanese_name})" if character.japanese_name else "")
                    present_characters_str_list.append(char_name)
                elif not character:
                     logger.warning(f"Character ID '{char_id}' listed in location '{location.id}' not found in world characters.")

        if present_characters_str_list:
            description_parts.append(f"Characters: {', '.join(present_characters_str_list)}.")
        # Optional: Add 'Nobody else is here.' if list is empty?

        # Process vocabulary for the location description itself
        # Consider if vocab should be processed *before* adding items/chars, or after
        # self.process_vocabulary(game_state, " ".join(description_parts)) # Moved processing if needed

        return "\\n".join(description_parts)

    def look_command(self, game_state: GameState, target: Optional[str] = None) -> Tuple[str, GameState]:
        """Handle the look command."""
        player = game_state.player
        world = game_state.world
        location = world.locations.get(player.current_location)

        if not location:
             logger.error(f"Look command failed: Player location ID '{player.current_location}' not found.")
             return "You are lost in a void. Something is terribly wrong.", game_state

        if target:
            # Try to find the target (item or character) in the current location or inventory
            target_id = target.lower() # Normalize target name

            # Check items in location
            for item_id in location.items:
                item = world.items.get(item_id)
                if item and (item.name.lower() == target_id or item.id.lower() == target_id):
                    desc = item.description + (f" ({item.japanese_description})" if item.japanese_description else "")
                    # Maybe add vocabulary processing for item description here?
                    # self.process_vocabulary(game_state, desc)
                    return desc, game_state

            # Check items in inventory
            for item_id in player.inventory:
                 item = world.items.get(item_id)
                 if item and (item.name.lower() == target_id or item.id.lower() == target_id):
                    desc = item.description + (f" ({item.japanese_description})" if item.japanese_description else "")
                    # Maybe add vocabulary processing for item description here?
                    # self.process_vocabulary(game_state, desc)
                    return desc, game_state

            # Check characters in location
            for char_id in location.characters:
                character = world.characters.get(char_id)
                if character and (character.name.lower() == target_id or character.id.lower() == target_id):
                    desc = character.description + (f" ({character.japanese_description})" if character.japanese_description else "")
                     # Maybe add vocabulary processing for character description here?
                     # self.process_vocabulary(game_state, desc)
                    return desc, game_state

            return f"You don't see '{target}' here.", game_state
        else:
            # Look around the location - use the updated description method
            desc = self.get_location_description(game_state)
            location = world.locations.get(player.current_location) # Get location object again
            # Process vocabulary associated with the location itself
            if location and hasattr(location, 'vocabulary') and location.vocabulary:
                # Call process_vocabulary correctly with the list and source ID
                vocab_string = self.process_vocabulary(game_state, location.vocabulary, location.id)
                if vocab_string: # Append the returned vocab info string if it's not empty
                    desc += vocab_string # Append the [Vocabulary] section
            return desc, game_state
    
    def take_command(self, item_name: str, game_state: GameState) -> Tuple[str, GameState]:
        """Take an item from the current location"""
        if not item_name:
            return "What do you want to take?", game_state
        
        current_loc_id = game_state.player.current_location
        current_loc = self.ensure_valid_location(current_loc_id, game_state)
        
        # Look for the item in the current location
        for item_id in current_loc.items:
            item = game_state.world.items.get(item_id)
            if item and not getattr(item, 'hidden', False) and (item_name in item.name.lower() or (item.japanese_name and item_name in item.japanese_name.lower())):
                if not getattr(item, 'can_be_taken', True):
                    return f"You can't take {item.name}.", game_state
                
                # Remove from location and add to inventory
                current_loc.items.remove(item_id)
                game_state.player.inventory.append(item_id)
                
                # Update player stats
                if hasattr(game_state.player, 'stats') and hasattr(game_state.player.stats, "items_collected"):
                    game_state.player.stats.items_collected += 1
                
                # Check for quest triggers when collecting an item
                quest_messages = []
                progress_messages = []
                
                try:
                    quest_messages, game_state = self.quest_handler.check_quest_triggers(
                        game_state, "collect_item", item_id
                    )
                except Exception as e:
                    logger.error(f"Error checking quest triggers for item {item_id}: {str(e)}")
                
                # Update quest progress
                try:
                    progress_messages, game_state = self.quest_handler.update_quest_progress(
                        game_state, "collect_item", item_id
                    )
                except Exception as e:
                    logger.error(f"Error updating quest progress for item {item_id}: {str(e)}")
                
                # Base message
                response = f"You take {item.name}."
                
                # Add quest messages if any
                if quest_messages:
                    response += "\n\n" + "\n".join(quest_messages)
                if progress_messages:
                    response += "\n\n" + "\n".join(progress_messages)
                
                return response, game_state
        
        return f"You don't see {item_name} here.", game_state
    
    def drop_command(self, item_name: str, game_state: GameState) -> Tuple[str, GameState]:
        """Drop an item from inventory to the current location"""
        if not item_name:
            return "What do you want to drop?", game_state
        
        current_loc_id = game_state.player.current_location
        current_loc = self.ensure_valid_location(current_loc_id, game_state)
        
        # Look for the item in inventory
        for item_id in game_state.player.inventory:
            item = game_state.world.items.get(item_id)
            if item and (item_name in item.name.lower() or (item.japanese_name and item_name in item.japanese_name.lower())):
                # Remove from inventory and add to location
                game_state.player.inventory.remove(item_id)
                current_loc.items.append(item_id)
                
                # Check for quest triggers for dropping an item
                quest_messages = []
                progress_messages = []
                
                try:
                    quest_messages, game_state = self.quest_handler.check_quest_triggers(
                        game_state, "drop_item", item_id
                    )
                except Exception as e:
                    logger.error(f"Error checking quest triggers for dropped item {item_id}: {str(e)}")
                
                # Update quest progress
                try:
                    progress_messages, game_state = self.quest_handler.update_quest_progress(
                        game_state, "drop_item", item_id
                    )
                except Exception as e:
                    logger.error(f"Error updating quest progress for dropped item {item_id}: {str(e)}")
                
                # Base message
                response = f"You drop {item.name}."
                
                # Add quest messages if any
                if quest_messages:
                    response += "\n\n" + "\n".join(quest_messages)
                if progress_messages:
                    response += "\n\n" + "\n".join(progress_messages)
                
                return response, game_state
        
        return f"You don't have {item_name}.", game_state
    
    def inventory_command(self, game_state: GameState) -> Tuple[str, GameState]:
        """Show the player's inventory"""
        if not game_state.player.inventory:
            return "Your inventory is empty.", game_state
        
        response = "Inventory (持ち物):\n"
        for item_id in game_state.player.inventory:
            item = game_state.world.items.get(item_id)
            if item:
                response += f"- {item.name}"
                if item.japanese_name:
                    response += f" ({item.japanese_name})"
                response += "\n"
        
        return response, game_state
    
    def use_command(self, item_name: str, game_state: GameState) -> Tuple[str, GameState]:
        """Use an item from inventory"""
        if not item_name:
            return "What do you want to use?", game_state
        
        # Look for the item in inventory
        for item_id in game_state.player.inventory:
            item = game_state.world.items.get(item_id)
            if item and (item_name in item.name.lower() or (item.japanese_name and item_name in item.japanese_name.lower())):
                # Check if it's a key
                if item.item_type == ItemType.KEY:
                    # Look for a locked location connected to the current one
                    current_loc = game_state.world.locations.get(game_state.player.current_location)
                    for direction, target_id in current_loc.connections.items():
                        target_loc = game_state.world.locations.get(target_id)
                        if target_loc and target_loc.requires_key == item_id:
                            # Unlock the location
                            target_loc.requires_key = None
                            
                            # Update quest progress
                            progress_messages, game_state = self.quest_handler.update_quest_progress(
                                game_state, "use_item", item_id
                            )
                            
                            # Base message
                            response = f"You use {item.name} to unlock the passage to the {direction}."
                            
                            # Add quest messages if any
                            if locals().get('progress_messages') and progress_messages:
                                response += "\n\n" + "\n".join(progress_messages)
                            
                            return response, game_state
                
                # Check for custom item effects
                if "use_effect" in item.properties:
                    effect = item.properties["use_effect"]
                    
                    # Update quest progress
                    progress_messages, game_state = self.quest_handler.update_quest_progress(
                        game_state, "use_item", item_id
                    )
                    
                    # Base message
                    response = f"You use {item.name}. {effect}"
                    
                    # Add quest messages if any
                    if locals().get('progress_messages') and progress_messages:
                        response += "\n\n" + "\n".join(progress_messages)
                    
                    return response, game_state
                
                return f"You're not sure how to use {item.name} here.", game_state
        
        return f"You don't have {item_name}.", game_state
    
    def talk_command(self, character_name: str, game_state: GameState) -> Tuple[str, GameState]:
        """Talk to a character in the current location"""
        if not character_name:
            return "Who do you want to talk to?", game_state
        
        current_loc = game_state.world.locations.get(game_state.player.current_location)
        if not current_loc:
            return "Error: Current location not found.", game_state
        
        # Look for the character in the current location
        for char_id in current_loc.characters:
            char = game_state.world.characters.get(char_id)
            if char and (character_name in char.name.lower() or (char.japanese_name and character_name in char.japanese_name.lower())):
                # Check for quest triggers when talking to an NPC
                quest_messages, game_state = self.quest_handler.check_quest_triggers(
                    game_state, "talk_to_npc", char_id
                )
                
                # Update quest progress
                progress_messages, game_state = self.quest_handler.update_quest_progress(
                    game_state, "talk_to_npc", char_id
                )
                
                # Get dialogue based on active quests
                dialogue_response = ""
                for quest_id in char.quest_ids:
                    if quest_id in game_state.quest_log.active_quests:
                        quest = game_state.quest_log.active_quests[quest_id]
                        if quest_id in char.quest_dialogues and quest.state.value in char.quest_dialogues[quest_id]:
                            dialogue = char.quest_dialogues[quest_id][quest.state.value]
                            dialogue_response = f"{char.name}: {dialogue.get('response', '')}"
                            if "japanese_response" in dialogue:
                                dialogue_response += f"\n\n{dialogue['japanese_response']}"
                
                # If no quest dialogue, use default
                if not dialogue_response:
                    if "default" in char.dialogues:
                        dialogue_response = f"{char.name}: {char.dialogues['default'].get('response', '')}"
                        jp_response = char.dialogues["default"].get("japanese_response", "")
                        if jp_response:
                            dialogue_response += f"\n\n{jp_response}"
                        
                        # List available topics
                        if len(char.dialogues) > 1:
                            dialogue_response += "\n\nYou can ask about: "
                            topics = [topic for topic in char.dialogues.keys() if topic != "default"]
                            dialogue_response += ", ".join(topics)
                    else:
                        dialogue_response = f"{char.name} looks at you but doesn't say anything."
                
                # Learn vocabulary from the character
                if char.vocabulary:
                    dialogue_response += self.process_vocabulary(game_state, char.vocabulary, char_id)
                
                # Add quest messages if any
                if locals().get('quest_messages') and quest_messages:
                    dialogue_response += "\n\n" + "\n".join(quest_messages)
                if locals().get('progress_messages') and progress_messages:
                    dialogue_response += "\n\n" + "\n".join(progress_messages)
                
                return dialogue_response, game_state
        
        return f"You don't see {character_name} here.", game_state
    
    def help_command(self, game_state: GameState) -> Tuple[str, GameState]:
        """Display help information"""
        help_text = """
Available Commands:
- north/south/east/west/up/down: Move in that direction (n/s/e/w/u/d for short)
- look [object]: Look at your surroundings or examine a specific object
- take [item]: Pick up an item
- drop [item]: Drop an item from your inventory
- inventory: Check what you're carrying (i for short)
- use [item]: Use an item in your inventory
- talk [character]: Talk to someone
- quests: View your active quests
- grammar [challenge_id]: Start a grammar challenge or list available challenges
- help: Show this help message

Japanese Commands:
- 北/南/東/西/上/下: Move in that direction
- 見る [object]: Look at something
- 取る [item]: Pick up an item
- 置く [item]: Drop an item
- 持ち物: Check inventory
- 使う [item]: Use an item
- 話す [character]: Talk to someone
- クエスト: View quests
- 文法 [challenge_id]: Grammar practice
- ヘルプ: Show help
"""
        return help_text, game_state
    
    def quest_command(self, quest_id: str, game_state: GameState) -> Tuple[str, GameState]:
        """Show information about quests"""
        quest_info = self.quest_handler.get_quest_info(game_state, quest_id.strip() if quest_id else None)
        return quest_info, game_state
    
    def process_vocabulary(self, game_state: GameState, vocabulary_list: List[Dict[str, str]], source_id: str) -> str:
        """
        Process vocabulary items from an entity and add them to the player's learned vocabulary
        
        Args:
            game_state: Current game state
            vocabulary_list: List of vocabulary items
            source_id: ID of the source entity (location, item, NPC)
            
        Returns:
            String containing vocabulary information
        """
        if not vocabulary_list:
            return ""
        
        now = datetime.now().isoformat()
        vocab_info = "\n\n[Vocabulary]"
        new_words = 0
        
        for vocab_item in vocabulary_list:
            japanese = vocab_item.get("japanese", "")
            if not japanese:
                continue
                
            english = vocab_item.get("english", "")
            reading = vocab_item.get("reading", "")
            
            # Generate a vocab ID
            vocab_id = f"vocab_{len(game_state.world.vocabulary)}"
            
            # Check if this is a new vocabulary item for the player
            if vocab_id not in game_state.player.learned_vocabulary:
                # Add to player's learned vocabulary
                game_state.player.learned_vocabulary[vocab_id] = LearnedVocabulary(
                    vocabulary_id=vocab_id,
                    first_encountered_location=game_state.player.current_location,
                    first_encountered_time=now,
                    mastery_level=1,
                    context=f"From {source_id}"
                )
                
                # Add to world vocabulary if not already there
                if vocab_id not in game_state.world.vocabulary:
                    game_state.world.vocabulary[vocab_id] = VocabularyEntry(
                        japanese=japanese,
                        english=english,
                        reading=reading,
                        part_of_speech=vocab_item.get("part_of_speech", ""),
                        example_sentence=vocab_item.get("example_sentence", ""),
                        notes=vocab_item.get("notes", "")
                    )
                
                # Update player stats
                if hasattr(game_state.player.stats, "vocabulary_learned"):
                    game_state.player.stats.vocabulary_learned += 1
                
                new_words += 1
                
                # Add to vocabulary info
                vocab_info += f"\n- {japanese}"
                if reading:
                    vocab_info += f" ({reading})"
                vocab_info += f": {english}"
        
        if new_words > 0:
            return vocab_info
        else:
            return ""
    
    def grammar_challenge_command(self, challenge_id: str, game_state: GameState) -> Tuple[str, GameState]:
        """Handle grammar challenge commands"""
        # If no challenge ID specified, list available challenges
        if not challenge_id:
            active_grammar_challenges = []
            
            # Find grammar challenges in active quests
            for quest_id, quest in game_state.quest_log.active_quests.items():
                for objective in quest.objectives:
                    if (objective.type == ObjectiveType.GRAMMAR_CHALLENGE and 
                        not objective.completed):
                        active_grammar_challenges.append({
                            "id": objective.target_id,
                            "description": objective.description,
                            "quest": quest.title
                        })
            
            if not active_grammar_challenges:
                return "You don't have any active grammar challenges.", game_state
            
            response = "Available grammar challenges:\n"
            for i, challenge in enumerate(active_grammar_challenges, 1):
                response += f"{i}. {challenge['description']} (Quest: {challenge['quest']})\n"
                response += f"   Type 'grammar {challenge['id']}' to start\n"
            
            return response, game_state
        
        # Find the specific grammar challenge
        for quest_id, quest in game_state.quest_log.active_quests.items():
            for objective in quest.objectives:
                if (objective.type == ObjectiveType.GRAMMAR_CHALLENGE and 
                    objective.target_id == challenge_id and
                    not objective.completed):
                    
                    # Set this as the active challenge
                    game_state.active_grammar_challenge = {
                        "quest_id": quest_id,
                        "objective_id": objective.id,
                        "target_id": objective.target_id
                    }
                    
                    # Return the prompt
                    prompt = objective.properties.get("prompt", "Complete the grammar challenge")
                    response = f"Grammar Challenge: {objective.description}\n\n{prompt}"
                    
                    return response, game_state
        
        return f"Grammar challenge '{challenge_id}' not found or already completed.", game_state
    
    def process_grammar_answer(self, answer: str, game_state: GameState) -> Tuple[str, GameState]:
        """Process an answer to a grammar challenge"""
        if not hasattr(game_state, 'active_grammar_challenge') or not game_state.active_grammar_challenge:
            return "No active grammar challenge.", game_state
        
        quest_id = game_state.active_grammar_challenge["quest_id"]
        target_id = game_state.active_grammar_challenge["target_id"]
        
        # Process the answer
        messages, updated_game_state = self.quest_handler.update_quest_progress(
            game_state, "grammar_challenge", target_id, answer
        )
        
        # Clear the active challenge
        if messages:  # If there was a response (completed or feedback)
            # Check if the objective was completed
            was_completed = False
            for message in messages:
                if "Grammar challenge completed" in message:
                    was_completed = True
                    break
            
            if was_completed:
                updated_game_state.active_grammar_challenge = None
        
        return "\n".join(messages) if messages else "No response from the challenge.", updated_game_state 