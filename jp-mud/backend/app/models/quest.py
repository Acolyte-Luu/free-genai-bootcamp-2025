from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field


class ObjectiveType(str, Enum):
    VISIT_LOCATION = "visit_location"  # Visit a specific location
    COLLECT_ITEM = "collect_item"      # Add an item to inventory
    TALK_TO_NPC = "talk_to_npc"        # Talk to a specific NPC
    USE_ITEM = "use_item"              # Use an item in a specific location
    LEARN_VOCABULARY = "learn_vocabulary"  # Learn a set of vocabulary words
    GRAMMAR_CHALLENGE = "grammar_challenge"  # Complete a grammar challenge
    CUSTOM = "custom"                  # Custom objective with special conditions


class RewardType(str, Enum):
    ITEM = "item"                      # Receive an item
    UNLOCK_LOCATION = "unlock_location"  # Unlock a new location
    LEARN_SKILL = "learn_skill"        # Learn a new skill or ability
    VOCABULARY_BOOST = "vocabulary_boost"  # Unlock new vocabulary
    CUSTOM = "custom"                  # Custom reward


class QuestObjective(BaseModel):
    id: str
    type: ObjectiveType
    description: str
    japanese_description: str
    target_id: str                     # Location ID, item ID, NPC ID, etc.
    count: int = 1                     # Number required (for collection quests)
    completed: bool = False
    progress: int = 0                  # Current progress toward completion
    hints: List[str] = Field(default_factory=list)
    japanese_hints: List[str] = Field(default_factory=list)
    vocabulary: List[Dict[str, str]] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)  # Additional properties for special objectives


class QuestReward(BaseModel):
    type: RewardType
    description: str
    japanese_description: str
    target_id: Optional[str] = None    # Item ID, location ID, etc.
    quantity: int = 1
    claimed: bool = False
    vocabulary: List[Dict[str, str]] = Field(default_factory=list)


class QuestState(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Quest(BaseModel):
    id: str
    title: str
    japanese_title: str
    description: str
    japanese_description: str
    state: QuestState = QuestState.NOT_STARTED
    objectives: List[QuestObjective] = Field(default_factory=list)
    rewards: List[QuestReward] = Field(default_factory=list)
    prerequisite_quests: List[str] = Field(default_factory=list)
    start_location: Optional[str] = None
    completion_location: Optional[str] = None
    start_dialogue: Optional[Dict[str, str]] = None
    completion_dialogue: Optional[Dict[str, str]] = None
    difficulty: int = 1  # 1-5 scale, affects language complexity
    jlpt_level: Optional[int] = None  # JLPT level (5-1, where 5 is easiest)
    time_limit: Optional[int] = None  # Time limit in seconds, if any
    hidden: bool = False  # If true, quest is not shown until discovered


class QuestLog(BaseModel):
    active_quests: Dict[str, Quest] = Field(default_factory=dict)
    completed_quests: Dict[str, Quest] = Field(default_factory=dict)
    failed_quests: Dict[str, Quest] = Field(default_factory=dict)
    available_quests: Dict[str, Quest] = Field(default_factory=dict)  # Discovered but not started 