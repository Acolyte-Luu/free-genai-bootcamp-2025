import axios from 'axios';

// Define the API base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8020/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// World Structure Types
export interface Location {
  id: string;
  name: string;
  japanese_name: string;
  description: string;
  japanese_description: string;
  connections: Record<string, string>;
  characters: string[];
  items: string[];
  vocabulary: VocabularyItem[];
  visited: boolean;
  requires_key?: string;
}

export interface Character {
  id: string;
  name: string;
  japanese_name: string;
  description: string;
  japanese_description: string;
  dialogues: Record<string, DialogueEntry>;
  vocabulary: VocabularyItem[];
  items: string[];
  quest_ids: string[];
}

export interface DialogueEntry {
  response: string;
  japanese_response: string;
}

export interface Item {
  id: string;
  name: string;
  japanese_name: string;
  description: string;
  japanese_description: string;
  type: string;
  properties: Record<string, unknown>;
  vocabulary: VocabularyItem[];
  can_be_taken: boolean;
  hidden: boolean;
}

export interface VocabularyItem {
  japanese: string;
  english: string;
  reading?: string;
  part_of_speech?: string;
  example_sentence?: string;
  notes?: string;
}

export interface QuestObjective {
  id: string;
  type: string;
  description: string;
  japanese_description: string;
  target_id: string;
  count: number;
  completed: boolean;
  progress: number;
  properties?: Record<string, any>;
  vocabulary: VocabularyItem[];
}

export interface QuestReward {
  type: string;
  description: string;
  japanese_description: string;
  target_id?: string;
  quantity: number;
  claimed: boolean;
  vocabulary: VocabularyItem[];
}

export interface Quest {
  id: string;
  title: string;
  japanese_title: string;
  description: string;
  japanese_description: string;
  state: string;
  objectives: QuestObjective[];
  rewards: QuestReward[];
  prerequisite_quests: string[];
  difficulty: number;
  jlpt_level?: number;
  hidden: boolean;
}

export interface QuestLog {
  active_quests: Record<string, Quest>;
  completed_quests: Record<string, Quest>;
  failed_quests: Record<string, Quest>;
  available_quests: Record<string, Quest>;
}

export interface GrammarChallenge {
  quest_id: string;
  objective_id: string;
  target_id: string;
}

export interface Player {
  current_location: string;
  inventory: string[];
  learned_vocabulary: Record<string, any>;
  knowledge?: Record<string, any>;
  stats: {
    quests_completed: number;
    locations_visited: string[];
    items_collected: number;
    vocabulary_learned: number;
    grammar_points_mastered: number;
    moves: number;
  };
}

export interface World {
  locations: Record<string, Location>;
  characters: Record<string, Character>;
  items: Record<string, Item>;
  vocabulary: Record<string, VocabularyItem>;
}

export interface GameState {
  world: World;
  player: Player;
  visited_locations: string[];
  flags: Record<string, boolean>;
  metadata: Record<string, unknown>;
  quest_log: QuestLog;
  active_grammar_challenge?: GrammarChallenge;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AvailableCommands {
  movement: string[];
  actions: string[];
  japanese_commands: string[];
}

// API Response Types
export interface GenerateWorldResponse {
  world: Record<string, unknown>;
}

export interface ProcessInputResponse {
  response: string;
  game_state: GameState;
  chat_history: ChatMessage[];
}

export interface ValidateJapaneseResponse {
  is_valid: boolean;
  feedback: string;
}

export interface SaveGameResponse {
  status: string;
  message: string;
  game_id?: string;
}

export interface LoadGameResponse {
  state: GameState;
  chat_history: ChatMessage[];
}

// API functions
export const gameApi = {
  // Generate a new game world
  generateWorld: async (prompt: string): Promise<GenerateWorldResponse> => {
    const response = await apiClient.post<GenerateWorldResponse>('/generate-world', { prompt });
    return response.data;
  },

  // Process user input
  processInput: async (
    input: string, 
    gameState: GameState, 
    chatHistory: ChatMessage[]
  ): Promise<ProcessInputResponse> => {
    const response = await apiClient.post<ProcessInputResponse>('/process-input', {
      input,
      game_state: gameState,
      chat_history: chatHistory,
    });
    return response.data;
  },

  // Validate Japanese text
  validateJapanese: async (text: string): Promise<ValidateJapaneseResponse> => {
    const response = await apiClient.post<ValidateJapaneseResponse>('/validate-japanese', { text });
    return response.data;
  },

  // Save game state
  saveGameState: async (
    gameState: GameState, 
    chatHistory: ChatMessage[]
  ): Promise<SaveGameResponse> => {
    const response = await apiClient.post<SaveGameResponse>('/save-state', {
      state: {
        world: gameState.world,
        player: gameState.player,
        visited_locations: Array.from(gameState.visited_locations),
        flags: gameState.flags,
        metadata: gameState.metadata,
        quest_log: gameState.quest_log,
        active_grammar_challenge: gameState.active_grammar_challenge
      },
      chat_history: chatHistory,
    });
    return response.data;
  },

  // Load game state
  loadGameState: async (gameId: string): Promise<LoadGameResponse> => {
    const response = await apiClient.post<LoadGameResponse>('/load-state', { game_id: gameId });
    return response.data;
  },
  
  // Get available commands
  getAvailableCommands: async (): Promise<AvailableCommands> => {
    const response = await apiClient.get<AvailableCommands>('/commands');
    return response.data;
  },
}; 