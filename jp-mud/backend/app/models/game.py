from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from app.models.quest import Quest, QuestLog


class Direction(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"
    IN = "in"
    OUT = "out"


class ItemType(str, Enum):
    GENERAL = "general"
    KEY = "key"
    WEAPON = "weapon"
    ARMOR = "armor"
    FOOD = "food"
    SCROLL = "scroll"
    BOOK = "book"
    QUEST = "quest"


class Item(BaseModel):
    id: str
    name: str
    japanese_name: str = ""
    description: str
    japanese_description: str = ""
    item_type: ItemType = ItemType.GENERAL
    properties: Dict[str, Any] = Field(default_factory=dict)
    vocabulary: List[Dict[str, str]] = Field(default_factory=list)
    can_be_taken: bool = True
    hidden: bool = False
    related_quest_id: Optional[str] = None  # Quest that this item is related to


class Character(BaseModel):
    id: str
    name: str
    japanese_name: str = ""
    description: str
    japanese_description: str = ""
    dialogues: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # topic -> {response, japanese_response}
    vocabulary: List[Dict[str, str]] = Field(default_factory=list)
    items: List[str] = Field(default_factory=list)  # Item IDs
    quest_ids: List[str] = Field(default_factory=list)  # Quests this NPC is associated with
    quest_dialogues: Dict[str, Dict[str, Dict[str, str]]] = Field(default_factory=dict)  # quest_id -> state -> {response, japanese_response}


class Location(BaseModel):
    id: str
    name: str
    japanese_name: str = ""
    description: str
    japanese_description: str = ""
    connections: Dict[str, str] = Field(default_factory=dict)  # direction -> location_id
    characters: List[str] = Field(default_factory=list)  # Character IDs present
    items: List[str] = Field(default_factory=list)  # Item IDs present
    vocabulary: List[Dict[str, str]] = Field(default_factory=list)
    visited: bool = False
    requires_key: Optional[str] = None  # Item ID required to enter
    quest_triggers: List[str] = Field(default_factory=list)  # Quest IDs triggered by visiting
    hidden: bool = False  # If true, not shown in connections until discovered


class VocabularyEntry(BaseModel):
    japanese: str
    english: str
    reading: Optional[str] = None
    part_of_speech: Optional[str] = None
    example_sentence: Optional[str] = None
    notes: Optional[str] = None
    jlpt_level: Optional[int] = None  # JLPT level (5-1, where 5 is easiest)
    mastery_level: int = 0  # 0-5 scale, 0 = not learned, 5 = mastered
    review_count: int = 0  # Number of times reviewed


class LearnedVocabulary(BaseModel):
    vocabulary_id: str
    first_encountered_location: Optional[str] = None
    first_encountered_time: Optional[str] = None
    mastery_level: int = 0  # 0-5 scale, 0 = not learned, 5 = mastered
    last_review_time: Optional[str] = None
    next_review_time: Optional[str] = None
    review_count: int = 0
    context: Optional[str] = None  # Context where this vocabulary was encountered


class PlayerStats(BaseModel):
    """Player statistics"""
    moves: int = 0
    items_collected: int = 0
    locations_visited: Set[str] = Field(default_factory=set)
    vocabulary_learned: int = 0
    grammar_points_mastered: int = 0
    quests_completed: int = 0
    jlpt_progress: Dict[int, float] = Field(default_factory=dict)  # {level: completion_percentage}
    time_played: float = 0  # Time in seconds


class Player(BaseModel):
    """Player state"""
    current_location: str
    inventory: List[str] = Field(default_factory=list)
    learned_vocabulary: Dict[str, LearnedVocabulary] = Field(default_factory=dict)
    knowledge: Dict[str, Any] = Field(default_factory=dict)  # Tracks grammar points and other knowledge
    quest_progress: Dict[str, Any] = Field(default_factory=dict)
    stats: PlayerStats = Field(default_factory=PlayerStats)
    jlpt_level: int = 5  # Current JLPT level (5 is lowest, 1 is highest)
    last_command: str = ""
    last_command_time: str = ""


class World(BaseModel):
    locations: Dict[str, Location] = Field(default_factory=dict)
    characters: Dict[str, Character] = Field(default_factory=dict)
    items: Dict[str, Item] = Field(default_factory=dict)
    vocabulary: Dict[str, VocabularyEntry] = Field(default_factory=dict)
    quests: Dict[str, Quest] = Field(default_factory=dict)  # All quests in the game


class GameState(BaseModel):
    world: World = Field(default_factory=World)
    player: Player = Field(default_factory=Player)
    visited_locations: Set[str] = Field(default_factory=set)
    flags: Dict[str, bool] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    quest_log: QuestLog = Field(default_factory=QuestLog)  # Player's quest log
    active_grammar_challenge: Optional[Dict[str, str]] = None  # Currently active grammar challenge 