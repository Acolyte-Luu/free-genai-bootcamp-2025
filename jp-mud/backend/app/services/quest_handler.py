from typing import Dict, List, Tuple, Any, Optional, Set
from datetime import datetime
from loguru import logger
import re

from app.models.game import GameState, Player, World, Location, Character, Item
from app.models.quest import (
    Quest, QuestObjective, QuestReward, QuestState, 
    ObjectiveType, RewardType, QuestLog
)


class QuestHandler:
    """
    Handles all quest-related functionality in the game
    """
    
    def __init__(self):
        pass
    
    def check_quest_triggers(self, game_state: GameState, trigger_type: str, entity_id: str) -> Tuple[List[str], GameState]:
        """
        Check if any quests are triggered by the player's actions
        
        Args:
            game_state: Current game state
            trigger_type: Type of trigger (visit_location, collect_item, talk_to_npc, etc.)
            entity_id: ID of the entity involved (location, item, NPC, etc.)
            
        Returns:
            List of messages about quests and updated game state
        """
        messages = []
        
        # Check location-based triggers
        if trigger_type == "visit_location":
            current_location = game_state.world.locations.get(entity_id)
            if current_location and current_location.quest_triggers:
                for quest_id in current_location.quest_triggers:
                    # Check if the quest exists and is not already started or completed
                    if (quest_id in game_state.world.quests and 
                        quest_id not in game_state.quest_log.active_quests and
                        quest_id not in game_state.quest_log.completed_quests):
                        
                        quest = game_state.world.quests[quest_id]
                        
                        # Check if prerequisites are met
                        prerequisites_met = True
                        for prereq_id in quest.prerequisite_quests:
                            if prereq_id not in game_state.quest_log.completed_quests:
                                prerequisites_met = False
                                break
                        
                        if prerequisites_met and not quest.hidden:
                            # Add quest to available quests
                            game_state.quest_log.available_quests[quest_id] = quest
                            messages.append(f"New quest available: {quest.title} - {quest.japanese_title}")
        
        # Check NPC-based triggers
        elif trigger_type == "talk_to_npc":
            npc = game_state.world.characters.get(entity_id)
            if npc and npc.quest_ids:
                for quest_id in npc.quest_ids:
                    # Check if quest exists and is available but not active
                    if (quest_id in game_state.world.quests and
                        quest_id in game_state.quest_log.available_quests and
                        quest_id not in game_state.quest_log.active_quests):
                        
                        quest = game_state.world.quests[quest_id]
                        
                        # Start the quest
                        quest.state = QuestState.IN_PROGRESS
                        game_state.quest_log.active_quests[quest_id] = quest
                        game_state.quest_log.available_quests.pop(quest_id)
                        
                        # Prepare quest start message
                        start_message = f"Quest started: {quest.title} - {quest.japanese_title}\n\n"
                        start_message += f"{quest.description}\n\n{quest.japanese_description}"
                        
                        # Add objective information
                        if quest.objectives:
                            start_message += "\n\nObjectives:"
                            for objective in quest.objectives:
                                start_message += f"\n- {objective.description}"
                        
                        messages.append(start_message)
        
        # Check item-based triggers
        elif trigger_type == "collect_item":
            item = game_state.world.items.get(entity_id)
            if item and item.related_quest_id:
                quest_id = item.related_quest_id
                
                # Check if quest exists but is not yet started
                if (quest_id in game_state.world.quests and
                    quest_id not in game_state.quest_log.active_quests and
                    quest_id not in game_state.quest_log.completed_quests):
                    
                    quest = game_state.world.quests[quest_id]
                    
                    # Add quest to available quests if prerequisites are met
                    prerequisites_met = True
                    for prereq_id in quest.prerequisite_quests:
                        if prereq_id not in game_state.quest_log.completed_quests:
                            prerequisites_met = False
                            break
                    
                    if prerequisites_met:
                        game_state.quest_log.available_quests[quest_id] = quest
                        messages.append(f"You found {item.name}. New quest available: {quest.title}")
        
        return messages, game_state
    
    def update_quest_progress(self, game_state: GameState, action_type: str, entity_id: str, input_text: str = None) -> Tuple[List[str], GameState]:
        """
        Update quest progress based on player actions
        
        Args:
            game_state: Current game state
            action_type: Type of action (visit_location, collect_item, talk_to_npc, etc.)
            entity_id: ID of the entity involved (location, item, NPC, etc.)
            input_text: Player's input text (for grammar challenges)
            
        Returns:
            List of messages about quest progress and updated game state
        """
        messages = []
        updated = False
        
        # Process active quests
        for quest_id, quest in list(game_state.quest_log.active_quests.items()):
            quest_updated = False
            
            # Check each objective
            for objective in quest.objectives:
                if objective.completed:
                    continue
                
                # Check if this action completes the objective
                if (objective.type == ObjectiveType.VISIT_LOCATION and 
                    action_type == "visit_location" and 
                    objective.target_id == entity_id):
                    
                    objective.completed = True
                    quest_updated = True
                    messages.append(f"Quest objective completed: {objective.description}")
                
                elif (objective.type == ObjectiveType.COLLECT_ITEM and 
                      action_type == "collect_item" and 
                      objective.target_id == entity_id):
                    
                    objective.progress += 1
                    if objective.progress >= objective.count:
                        objective.completed = True
                        messages.append(f"Quest objective completed: {objective.description}")
                    else:
                        messages.append(f"Quest progress: {objective.progress}/{objective.count} {objective.description}")
                    
                    quest_updated = True
                
                elif (objective.type == ObjectiveType.TALK_TO_NPC and 
                      action_type == "talk_to_npc" and 
                      objective.target_id == entity_id):
                    
                    objective.completed = True
                    quest_updated = True
                    messages.append(f"Quest objective completed: {objective.description}")
                
                elif (objective.type == ObjectiveType.USE_ITEM and 
                      action_type == "use_item" and 
                      objective.target_id == entity_id):
                    
                    objective.completed = True
                    quest_updated = True
                    messages.append(f"Quest objective completed: {objective.description}")
                
                elif (objective.type == ObjectiveType.GRAMMAR_CHALLENGE and 
                      action_type == "grammar_challenge" and 
                      objective.target_id == entity_id and 
                      input_text):
                    
                    # Check if the input matches the expected pattern
                    correct_answer = objective.properties.get("correct_pattern", "")
                    if correct_answer and (
                        # Exact match
                        input_text.strip() == correct_answer or 
                        # Pattern match
                        (objective.properties.get("use_pattern", False) and 
                         re.search(correct_answer, input_text))
                    ):
                        objective.completed = True
                        quest_updated = True
                        messages.append(f"Grammar challenge completed: {objective.description}")
                        
                        # Add the learned grammar point to player's knowledge
                        if objective.properties.get("grammar_point"):
                            if "grammar_points" not in game_state.player.knowledge:
                                game_state.player.knowledge["grammar_points"] = []
                            game_state.player.knowledge["grammar_points"].append(
                                objective.properties["grammar_point"]
                            )
                            messages.append(f"Grammar point learned: {objective.properties['grammar_point']['name']}")
                    else:
                        # Provide feedback for incorrect answers
                        hint = objective.properties.get("hint", "Try again with a different structure.")
                        messages.append(f"That's not quite right. {hint}")
            
            # Check if all objectives are completed
            if quest_updated:
                updated = True
                all_completed = True
                for objective in quest.objectives:
                    if not objective.completed:
                        all_completed = False
                        break
                
                if all_completed:
                    # Complete the quest
                    quest.state = QuestState.COMPLETED
                    game_state.quest_log.completed_quests[quest_id] = quest
                    game_state.quest_log.active_quests.pop(quest_id)
                    
                    # Update player stats
                    game_state.player.stats.quests_completed += 1
                    
                    # Prepare completion message
                    completion_message = f"Quest completed: {quest.title} - {quest.japanese_title}\n"
                    if quest.rewards:
                        completion_message += "Rewards:\n"
                        for reward in quest.rewards:
                            completion_message += f"- {reward.description}\n"
                            
                            # Process rewards
                            if reward.type == RewardType.ITEM and reward.target_id:
                                if reward.target_id in game_state.world.items:
                                    game_state.player.inventory.append(reward.target_id)
                                    reward.claimed = True
                                    completion_message += f"  Added {game_state.world.items[reward.target_id].name} to your inventory.\n"
                            
                            elif reward.type == RewardType.UNLOCK_LOCATION and reward.target_id:
                                if reward.target_id in game_state.world.locations:
                                    location = game_state.world.locations[reward.target_id]
                                    location.hidden = False
                                    reward.claimed = True
                                    completion_message += f"  Unlocked new location: {location.name}.\n"
                            
                            elif reward.type == RewardType.VOCABULARY_BOOST and reward.vocabulary:
                                for vocab in reward.vocabulary:
                                    vocab_id = f"vocab_{len(game_state.world.vocabulary)}"
                                    # Add new vocabulary to world and player's learned vocabulary
                                    # Implementation depends on how vocabulary is stored
                                    completion_message += f"  Learned new word: {vocab.get('japanese', '')} ({vocab.get('english', '')}).\n"
                    
                    messages.append(completion_message)
        
        # Only update the game state if something changed
        if updated:
            return messages, game_state
        else:
            return [], game_state
    
    def get_quest_info(self, game_state: GameState, quest_id: Optional[str] = None) -> str:
        """
        Get information about quests
        
        Args:
            game_state: Current game state
            quest_id: Optional quest ID to get specific info, otherwise get all active quests
            
        Returns:
            String containing quest information
        """
        if quest_id:
            # Get info about a specific quest
            if quest_id in game_state.quest_log.active_quests:
                quest = game_state.quest_log.active_quests[quest_id]
                info = f"Quest: {quest.title} - {quest.japanese_title}\n"
                info += f"{quest.description}\n\n{quest.japanese_description}\n\n"
                
                # Add objectives
                info += "Objectives:\n"
                for objective in quest.objectives:
                    checkmark = "✓" if objective.completed else "□"
                    if objective.count > 1:
                        info += f"{checkmark} {objective.description} ({objective.progress}/{objective.count})\n"
                    else:
                        info += f"{checkmark} {objective.description}\n"
                
                return info
            else:
                return f"Quest {quest_id} not found in active quests."
        else:
            # Get info about all active quests
            if not game_state.quest_log.active_quests:
                return "You don't have any active quests."
            
            info = "Active Quests:\n"
            for quest_id, quest in game_state.quest_log.active_quests.items():
                completed_objectives = sum(1 for obj in quest.objectives if obj.completed)
                total_objectives = len(quest.objectives)
                info += f"- {quest.title} ({completed_objectives}/{total_objectives})\n"
            
            info += "\nAvailable Quests:\n"
            if game_state.quest_log.available_quests:
                for quest_id, quest in game_state.quest_log.available_quests.items():
                    info += f"- {quest.title}\n"
            else:
                info += "No available quests.\n"
            
            info += f"\nCompleted Quests: {len(game_state.quest_log.completed_quests)}"
            
            return info 