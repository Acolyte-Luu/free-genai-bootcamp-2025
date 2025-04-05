import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os
import sys

# Add the app directory to the path for imports
# Adjust the path as necessary based on your test runner's working directory
# Assuming 'tests' is directly inside 'backend'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app instance from main.py
# We assume your main FastAPI app instance is named 'app' in 'app.main'
# If it's different, adjust the import accordingly.
try:
    from app.main import app
except ImportError as e:
    print(f"Error: Could not import 'app' from 'app.main': {e}")
    print("Ensure jp-mud/backend/app/main.py exists and contains a FastAPI instance named 'app'.")
    # Fallback or skip if app cannot be imported
    pytest.skip("Skipping tests because FastAPI app could not be imported.", allow_module_level=True)


client = TestClient(app)

@pytest.fixture
def initial_game_state_dict():
    """Provides a basic initial game state dictionary for testing."""
    # This should reflect the state *before* the action is taken
    # Based on the simulation state after Action 1 / before Action 4
    return {
        "world": {
            "locations": {
                "start": {
                    "id": "start",
                    "name": "Village Square",
                    "japanese_name": "村の広場",
                    "description": "A peaceful village square...",
                    "japanese_description": "平和な村の広場...",
                    "connections": {"north": "forest", "east": "shop", "west": "house", "south": "river"},
                    "characters": [],
                    "items": ["map"], # Map is in the location initially
                    "vocabulary": [{"japanese": "広場", "english": "square"}],
                    "visited": True,
                     # Added default values for potentially missing optional fields from model
                     "requires_key": None,
                     "quest_triggers": [],
                     "hidden": False
                },
                 "shop": { # Add other locations needed for context if any
                    "id": "shop", "name": "Old Shop", "items": ["compass"], "characters": ["shopkeeper"],
                     "japanese_name": "古い店", "description": "A shop.", "japanese_description": "店。",
                     "connections": {"west": "start"}, "vocabulary": [], "visited": False,
                     "requires_key": None, "quest_triggers": [], "hidden": False
                 },
                 "forest": {"id": "forest", "name": "Forest", "connections": {"south": "start"}, "items": [], "characters": [], "japanese_name": "森", "description": "Wood.", "japanese_description": "木。", "vocabulary": [], "visited": False, "requires_key": None, "quest_triggers": [], "hidden": False},
                 "house": {"id": "house", "name": "House", "connections": {"east": "start"}, "items": [], "characters": [], "japanese_name": "家", "description": "A house.", "japanese_description": "家。", "vocabulary": [], "visited": False, "requires_key": None, "quest_triggers": [], "hidden": False},
                 "river": {"id": "river", "name": "River", "connections": {"north": "start"}, "items": [], "characters": [], "japanese_name": "川", "description": "Water.", "japanese_description": "水。", "vocabulary": [], "visited": False, "requires_key": None, "quest_triggers": [], "hidden": False}

            },
            "characters": {
                 "shopkeeper": {
                     "id": "shopkeeper", "name": "Shopkeeper", "japanese_name": "店主",
                     "description": "An NPC.", "japanese_description": "NPC。",
                     "dialogues": {"default": {"response": "Hi", "japanese_response": "こんにちは"}},
                     "vocabulary": [], "items": [], "quest_ids": [], "quest_dialogues": {}
                 }
            },
            "items": {
                "map": {
                    "id": "map", "name": "Village Map", "japanese_name": "村の地図",
                    "description": "A map.", "japanese_description": "地図。",
                    "item_type": "general", "properties": {}, "vocabulary": [],
                    "can_be_taken": True, "hidden": False, "related_quest_id": None
                },
                "compass": {
                    "id": "compass", "name": "Ancient Compass", "japanese_name": "方位磁針",
                    "description": "A compass.", "japanese_description": "方位磁針。",
                    "item_type": "general", "properties": {}, "vocabulary": [],
                    "can_be_taken": True, "hidden": False, "related_quest_id": None
                    }
            },
            "vocabulary": {}, # Using dict for World model {id: VocabularyEntry}
            "quests": {} # Using dict for World model {id: Quest}
        },
        "player": {
            "current_location": "start",
            "inventory": [], # Player inventory is empty initially
            "learned_vocabulary": {},
            "knowledge": {},
            "quest_progress": {},
            "stats": {
                 "moves": 0, "items_collected": 0, "locations_visited": ["start"],
                 "vocabulary_learned": 0, "grammar_points_mastered": 0,
                 "quests_completed": 0, "jlpt_progress": {}, "time_played": 0.0
                 },
            "jlpt_level": 5,
            "last_command": "",
            "last_command_time": ""
        },
        "visited_locations": ["start"], # Should be Set, but JSON uses list
        "flags": {},
        "metadata": {},
        "quest_log": {"active_quests": {}, "completed_quests": {}}, # Matches QuestLog model
        "active_grammar_challenge": None
    }

@pytest.fixture
def expected_game_state_after_take_map(initial_game_state_dict):
    """Provides the expected game state dictionary after taking the map."""
    import copy
    # Deep copy to avoid modifying the original fixture dict
    expected_state = copy.deepcopy(initial_game_state_dict)

    # Apply the expected changes
    expected_state["player"]["inventory"].append("map") # Map is now in inventory
    # Ensure items list exists before trying to remove
    if "items" in expected_state["world"]["locations"]["start"]:
         expected_state["world"]["locations"]["start"]["items"].remove("map") # Map is removed from location
    else:
         # This case shouldn't happen based on initial state, but good practice
         print("Warning: 'items' key missing from start location in expected state setup.")


    # If taking an item increments a stat, reflect that here
    # Example: expected_state["player"]["stats"]["items_collected"] = 1

    return expected_state

# Patch the target method within the context where it's *looked up*
# If api.game imports llm_service = LLMService(), patch 'app.api.game.llm_service.process_game_input'
# Adjust the patch target if your import structure is different (e.g., 'app.services.llm_service.LLMService.process_game_input' if imported differently)
@patch('app.api.game.llm_service.process_game_input', new_callable=AsyncMock)
def test_process_input_take_map(
    mock_process_game_input,
    initial_game_state_dict,
    expected_game_state_after_take_map
):
    """
    Test processing the 'take map' command via the /process-input endpoint,
    mocking the LLMService interaction.
    """
    user_input = "地図を取る" # Or "take map" if testing English input mapping
    initial_chat_history = [{"role": "system", "content": "Welcome..."}]

    # Configure the mock return value
    # It should return the narrative and the *final* expected state dictionary
    mock_narrative = "You pick up the Village Map (村の地図)."
    # The mock directly returns the state *as if* the function calls were applied by the service
    mock_process_game_input.return_value = (mock_narrative, expected_game_state_after_take_map)

    # Make the API call to the TestClient
    # Ensure the path matches your FastAPI router configuration in main.py
    api_prefix = "/api" # CORRECTED: Matches the prefix used in main.py
    response = client.post(
        f"{api_prefix}/process-input",
        json={
            "input": user_input,
            "game_state": initial_game_state_dict,
            "chat_history": initial_chat_history
        }
    )

    # Assertions
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Response: {response.text}"
    response_data = response.json()

    # Check that the mock was called correctly
    try:
        mock_process_game_input.assert_awaited_once_with(
            user_input,
            initial_game_state_dict, # API passes the dict directly
            initial_chat_history
        )
    except AssertionError as e:
        pytest.fail(f"Mock process_game_input not called as expected: {e}")


    # Check the response content
    assert response_data["response"] == mock_narrative, \
        f"Expected narrative '{mock_narrative}', got '{response_data['response']}'"

    # Compare game states carefully - convert lists to sets for order-independent comparison if needed
    # For simplicity, direct dict comparison is used here. Consider deepdiff library for complex cases.
    assert response_data["game_state"] == expected_game_state_after_take_map, \
        "Returned game state does not match the expected state after taking the map."

    # Check chat history update
    expected_chat_history = initial_chat_history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": mock_narrative}
    ]
    assert response_data["chat_history"] == expected_chat_history, \
        "Chat history was not updated correctly."

# Example of a test case that might fail if setup is wrong
def test_api_route_exists():
     """Check if the basic API route gives a 404 or method not allowed, not a server error"""
     api_prefix = "/api" # CORRECTED: Matches the prefix used in main.py
     response = client.post(f"{api_prefix}/process-input", json={}) # Send empty json
     # Expecting 422 Unprocessable Entity due to missing fields, not 404 Not Found
     assert response.status_code == 422, f"Expected 422 Unprocessable Entity for missing body, got {response.status_code}"

# Fixtures and test for Quest Activation Scenario

@pytest.fixture
def initial_quest_state_dict(initial_game_state_dict):
    """Provides game state where player is at the elder's house, quest not started."""
    import copy
    state = copy.deepcopy(initial_game_state_dict)

    # Define the quest structure within the world data
    # This mimics how the world might be loaded or generated
    state["world"]["quests"] = {
        "mountain_quest": {
            "id": "mountain_quest",
            "title": "The Misty Mountain Legend",
            "japanese_title": "霧の山の伝説",
            "description": "Investigate the legend of a treasure hidden in the Misty Mountain.",
            "japanese_description": "霧の山に隠された宝の伝説を調査する。",
            "objectives": [
                {"description": "Speak to the Village Elder about the legend.", "japanese_description": "村長に伝説について話を聞く。", "completed": False},
                {"description": "Find a way to navigate the Misty Mountain.", "japanese_description": "霧の山をナビゲートする方法を見つける。", "completed": False},
                {"description": "Reach the summit of the Misty Mountain.", "japanese_description": "霧の山の頂上に到達する。", "completed": False}
            ],
            "rewards": {"experience": 100, "items": []},
            "giver_id": "elder",
            "start_conditions": {},
            "completion_conditions": {},
            # Use the enum value if QuestState enum is imported and used
            # "initial_state": QuestState.NOT_STARTED
            "initial_state": "NOT_STARTED" # Default state if not started
        }
    }

    # Define the elder character if not already present fully
    state["world"]["characters"]["elder"] = {
        "id": "elder", "name": "Village Elder", "japanese_name": "村長",
        "description": "Wise elder.", "japanese_description": "賢い長老。",
        "dialogues": {
            "default": {"response": "Greetings.", "japanese_response": "こんにちは"},
            "legend": {"response": "Ah, the legend...", "japanese_response": "ああ、伝説。。。"}
        },
        "vocabulary": [], "items": [], "quest_ids": ["mountain_quest"], "quest_dialogues": {}
    }

    # Define the house location if not present fully
    # Ensure all required fields from the Location model are present
    state["world"]["locations"]["house"] = {
        "id": "house", "name": "Traditional House", "japanese_name": "伝統的な家",
        "description": "A house.", "japanese_description": "家。",
        "connections": {"east": "start"}, "characters": ["elder"], "items": [],
        "vocabulary": [], "visited": False, "requires_key": None,
        "quest_triggers": [], "hidden": False
    }
    # Ensure player starts at the house for this test
    state["player"]["current_location"] = "house"
    # Use list for JSON compatibility, even if model uses Set
    if "house" not in state["visited_locations"]:
        state["visited_locations"].append("house")

    # Ensure quest log is initially empty or doesn't contain this quest
    state["quest_log"] = {"active_quests": {}, "completed_quests": {}}
    state["player"]["quest_progress"] = {}


    return state

@pytest.fixture
def expected_state_after_accept_quest(initial_quest_state_dict):
    """Provides the expected game state after accepting the mountain quest."""
    import copy
    # Start from the *quest* initial state, not the original game state dict
    state = copy.deepcopy(initial_quest_state_dict)

    # Define the expected state of the quest in the log and progress
    quest_id = "mountain_quest"
    active_quest_data = {
        "quest_id": quest_id,
        "title": "The Misty Mountain Legend", # Get from quest definition
        # Use the enum value if QuestState enum is imported and used
        # "state": QuestState.ACCEPTED,
        "state": "ACCEPTED",
        "current_objective_index": 0, # Assuming it starts at the first objective
        "objectives_status": [False, False, False] # All objectives initially incomplete
    }
    state["quest_log"]["active_quests"][quest_id] = active_quest_data
    state["player"]["quest_progress"][quest_id] = {
        "state": "ACCEPTED",
        "current_objective_index": 0
    }

    return state

# Patch the target method
@patch('app.api.game.llm_service.process_game_input', new_callable=AsyncMock)
def test_process_input_accept_quest(
    mock_process_game_input,
    initial_quest_state_dict,      # Use the quest-specific initial state
    expected_state_after_accept_quest # Use the quest-specific expected state
):
    """
    Test accepting a quest by talking to an NPC via the /process-input endpoint.
    """
    user_input = "talk to elder about legend"
    initial_chat_history = [{"role": "system", "content": "Welcome..."}] # Or history relevant to being in the house

    # Configure the mock return value
    # Ensure the narrative uses the actual dialogue response from the fixture
    elder_dialogue = initial_quest_state_dict["world"]["characters"]["elder"]["dialogues"]["legend"]["response"]
    mock_narrative = elder_dialogue + "\n\nQuest Added: The Misty Mountain Legend" # Example narrative construction
    # Mock returns the narrative and the *final* state after quest update
    mock_process_game_input.return_value = (mock_narrative, expected_state_after_accept_quest)

    # Make the API call
    api_prefix = "/api"
    response = client.post(
        f"{api_prefix}/process-input",
        json={
            "input": user_input,
            "game_state": initial_quest_state_dict, # Send the specific initial state
            "chat_history": initial_chat_history
        }
    )

    # Assertions
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Response: {response.text}"
    response_data = response.json()

    # Check mock call
    try:
        mock_process_game_input.assert_awaited_once_with(
            user_input,
            initial_quest_state_dict,
            initial_chat_history
        )
    except AssertionError as e:
        pytest.fail(f"Mock process_game_input not called as expected: {e}")

    # Check response narrative
    assert response_data["response"] == mock_narrative

    # Check the crucial part: quest log and progress in the returned game state
    returned_state = response_data["game_state"]
    quest_id = "mountain_quest"

    assert quest_id in returned_state["quest_log"]["active_quests"], "Quest not found in active quests log"
    assert returned_state["quest_log"]["active_quests"][quest_id]["state"] == "ACCEPTED", "Quest state in log is not ACCEPTED"
    assert returned_state["quest_log"]["active_quests"][quest_id]["current_objective_index"] == 0, "Quest objective index is incorrect"

    assert quest_id in returned_state["player"]["quest_progress"], "Quest not found in player progress"
    assert returned_state["player"]["quest_progress"][quest_id]["state"] == "ACCEPTED", "Quest state in progress is not ACCEPTED"

    # Optionally, do a full state comparison if needed, but focusing on the quest part is key
    # assert returned_state == expected_state_after_accept_quest, "Full game state mismatch"

    # Check chat history
    expected_chat_history = initial_chat_history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": mock_narrative}
    ]
    assert response_data["chat_history"] == expected_chat_history 