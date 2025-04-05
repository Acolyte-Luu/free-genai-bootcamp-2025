import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import ChatHistory from './ChatHistory';
import ChatInput from './ChatInput';
import SaveLoadControls from './SaveLoadControls';
import GrammarChallenge from './GrammarChallenge';
import PlayerProfile from './PlayerProfile';
import GameInstructions from './GameInstructions';
import { Button } from './ui/Button';
import { Input } from './ui/input';
import { gameApi, ChatMessage, GameState, World, Player, AvailableCommands } from '../services/api';
import { useJapaneseValidator } from '../hooks/useJapaneseValidator';
import WorldMap from './WorldMap';

// Error type for more structured error handling
interface GameError {
  type: 'connection' | 'world_generation' | 'command_processing' | 'japanese_validation' | 'save_load' | 'general';
  message: string;
  details?: string;
  recoverable: boolean;
}

// Helper function to transform world data (moved outside component)
const transformWorldData = (rawWorldData: any): World => {
  try {
    const worldData: World = {
      locations: {},
      characters: {},
      items: {},
      vocabulary: {}
    };
    
    // Convert locations array to record
    if (Array.isArray(rawWorldData.locations)) {
      rawWorldData.locations.forEach((location: any) => {
        if (location.id) {
          worldData.locations[location.id] = location;
        }
      });
    } else if (typeof rawWorldData.locations === 'object') {
      // Handle case where locations are already in object format
      worldData.locations = rawWorldData.locations;
    }
    
    // Convert characters array to record
    if (Array.isArray(rawWorldData.characters)) {
      rawWorldData.characters.forEach((character: any) => {
        if (character.id) {
          worldData.characters[character.id] = character;
        }
      });
    } else if (typeof rawWorldData.characters === 'object') {
      worldData.characters = rawWorldData.characters;
    }
    
    // Convert items array to record
    if (Array.isArray(rawWorldData.items)) {
      rawWorldData.items.forEach((item: any) => {
        if (item.id) {
          worldData.items[item.id] = item;
        }
      });
    } else if (typeof rawWorldData.items === 'object') {
      worldData.items = rawWorldData.items;
    }
    
    // Convert vocabulary array to record (if it exists)
    if (Array.isArray(rawWorldData.vocabulary)) {
      rawWorldData.vocabulary.forEach((vocab: any, index: number) => {
        const id = vocab.id || `vocab_${index}`;
        worldData.vocabulary[id] = vocab;
      });
    } else if (typeof rawWorldData.vocabulary === 'object') {
      worldData.vocabulary = rawWorldData.vocabulary;
    }
    
    // Validate that we have at least a start location
    if (!worldData.locations['start']) {
      console.warn("No start location found in world data, creating a placeholder");
      worldData.locations['start'] = {
        id: 'start',
        name: 'Starting Area',
        japanese_name: '開始エリア',
        description: 'A mysterious starting point for your adventure.',
        japanese_description: '冒険の不思議な出発点。',
        connections: {},
        characters: [],
        items: [],
        vocabulary: [],
        visited: false
      };
    }
    
    return worldData;
  } catch (err) {
    console.error("Error transforming world data:", err);
    // Return minimal viable world structure
    return {
      locations: {
        'start': {
          id: 'start',
          name: 'Emergency Fallback Location',
          japanese_name: '緊急避難場所',
          description: 'Something went wrong with the world generation. This is a fallback location.',
          japanese_description: '世界の生成に問題が発生しました。これは緊急避難場所です。',
          connections: {},
          characters: [],
          items: [],
          vocabulary: [],
          visited: false
        }
      },
      characters: {},
      items: {},
      vocabulary: {}
    };
  }
};

// Error notification component
const ErrorNotification = ({ error, onDismiss }: { error: GameError, onDismiss: () => void }) => {
  // Determine styling based on error type
  const getErrorClass = () => {
    switch (error.type) {
      case 'connection':
        return 'bg-red-100 dark:bg-red-900 border-red-500 text-red-700 dark:text-red-300';
      case 'world_generation':
        return 'bg-orange-100 dark:bg-orange-900 border-orange-500 text-orange-700 dark:text-orange-300';
      default:
        return 'bg-yellow-100 dark:bg-yellow-900 border-yellow-500 text-yellow-700 dark:text-yellow-300';
    }
  };
  
  return (
    <div 
      className={`${getErrorClass()} border-l-4 p-4 rounded mb-4`} 
      role="alert"
      aria-live="assertive"
    >
      <div className="flex justify-between items-start">
        <div>
          <p className="font-bold">{error.message}</p>
          {error.details && <p className="text-sm mt-1">{error.details}</p>}
          {error.recoverable && (
            <p className="text-sm mt-2">
              {error.type === 'connection' 
                ? 'Check your internet connection and try again.' 
                : 'Try again or restart the game.'}
            </p>
          )}
        </div>
        <button 
          onClick={onDismiss}
          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          aria-label="Dismiss"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

const GameContainer = () => {
  const [gameState, setGameState] = useState<GameState | undefined>(undefined);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      role: 'system' as const,
      content: 'Welcome to the Japanese MUD! Type "start" to begin a new adventure.',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<GameError | undefined>(undefined);
  const [isWorldGenerated, setIsWorldGenerated] = useState(false);
  const [validationFeedback, setValidationFeedback] = useState<string | null>(null);
  const [availableCommands, setAvailableCommands] = useState<AvailableCommands | undefined>(undefined);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isInstructionsOpen, setIsInstructionsOpen] = useState(false);
  const [isMapVisible, setIsMapVisible] = useState(false);
  const [rawWorldData, setRawWorldData] = useState<any>(null);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const { validateJapanese, isValidating } = useJapaneseValidator();
  
  // Break circular dependencies with refs
  const handleNewGameRef = useRef<() => Promise<void>>(async () => {});
  const handleUserInputRef = useRef<(input: string) => Promise<void>>(async () => {});

  // Use useMemo to transform world data only when rawWorldData changes
  const transformedWorldData = useMemo(() => {
    if (!rawWorldData) return null;
    console.log("Transforming world data");
    return transformWorldData(rawWorldData);
  }, [rawWorldData]);

  // Define handleNewGame - reference via ref to break circular dependency
  handleNewGameRef.current = async () => {
    setIsLoading(true);
    setError(undefined);
    setValidationFeedback(null);
    setIsWorldGenerated(false); // Reset world generated state
    setRawWorldData(null); // Clear any existing world data
    
    try {
      const prompt = "Create a fantasy medieval world with Japanese elements";
      const result = await gameApi.generateWorld(prompt);
      
      console.log("World data from API:", result.world);
      
      // Check if we got a valid world structure
      if (!result.world || (typeof result.world !== 'object')) {
        throw new Error("Received invalid world data structure");
      }
      
      // Reset connection attempts on successful connection
      setConnectionAttempts(0);
      
      // Store the raw world data from API, transformation happens in useMemo
      setRawWorldData(result.world);
    } catch (err: any) {
      console.error(err);
      
      // Track connection attempts
      if (err.message?.includes('Failed to fetch') || err.name === 'NetworkError') {
        setConnectionAttempts(prev => prev + 1);
        
        setError({
          type: 'connection',
          message: 'Connection to game server failed',
          details: connectionAttempts > 0 
            ? `Failed after ${connectionAttempts + 1} attempts. Server may be down or unreachable.` 
            : 'Check your internet connection and try again.',
          recoverable: true
        });
      } else {
        setError({
          type: 'world_generation',
          message: 'Failed to create a new game world',
          details: err.message || 'Unknown error occurred during world generation',
          recoverable: true
        });
      }
      
      // If we've failed 3+ times, create a minimal fallback world to allow gameplay
      if (connectionAttempts >= 2) {
        console.log("Creating fallback world due to repeated connection failures");
        setRawWorldData({
          locations: [
            {
              id: "start",
              name: "Offline Starting Village",
              japanese_name: "オフライン開始村",
              description: "A simple village created for offline play. The server couldn't be reached, but you can still explore this basic world.",
              japanese_description: "オフラインプレイ用の簡単な村。サーバーに接続できませんでしたが、この基本的な世界を探索できます。",
              connections: {},
              characters: [],
              items: [],
              vocabulary: [],
              visited: false
            }
          ],
          characters: [],
          items: [],
          vocabulary: []
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Define the handleUserInput - reference via ref to break circular dependency
  handleUserInputRef.current = async (input: string) => {
    if (!input.trim()) return;
    
    setIsLoading(true);
    setError(undefined); // Clear errors at the start of processing input
    setValidationFeedback(null);
    
    try {
      // If we haven't generated a world yet, handle the "start" command
      if (input.toLowerCase() === "start" && !isWorldGenerated) {
        await handleNewGameRef.current?.();
        return;
      }
      
      // We need a valid game state to proceed
      if (!gameState) {
        setError({
          type: 'general',
          message: 'Game state not initialized',
          details: 'Please start a new game with the "start" command',
          recoverable: true
        });
        setIsLoading(false);
        return;
      }
      
      // Check if we need to validate Japanese text
      const hasJapaneseChars = /[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]/.test(input);
      
      // Only validate when text contains Japanese characters
      if (hasJapaneseChars) {
        try {
          const result = await gameApi.validateJapanese(input);
          if (!result.is_valid) {
            setValidationFeedback(result.feedback);
            setIsLoading(false);
            return; // Don't proceed if Japanese is invalid
          }
        } catch (validationErr: any) {
          console.error("Japanese validation error:", validationErr);
          // Continue without validation if it fails - better UX than blocking
          setChatHistory(prev => [...prev, {
            role: 'system',
            content: 'Japanese validation is currently unavailable. Your input will be processed as is.'
          }]);
        }
      }
      
      // Add user input to chat history immediately for better UX
      setChatHistory(prev => [
        ...prev,
        { role: 'user', content: input }
      ]);
      
      // Process the input through the game engine
      const result = await gameApi.processInput(input, gameState, [
        ...chatHistory,
        { role: 'user', content: input }
      ]);
      
      // Update game state and chat history in a single batch
      setGameState(result.game_state);
      setChatHistory(result.chat_history);
    } catch (err: any) {
      console.error("Error processing command:", err);
      
      // Handle specific error types
      if (err.message?.includes('Failed to fetch') || err.name === 'NetworkError') {
        setChatHistory(prev => [...prev, {
          role: 'system',
          content: 'Unable to reach the game server. Your command was not processed. If this persists, the game will continue in offline mode with limited functionality.'
        }]);
        
        // Track connection failures
        setConnectionAttempts(prev => prev + 1);
        
        // If multiple connection failures, switch to offline mode
        if (connectionAttempts >= 2) {
          setChatHistory(prev => [...prev, {
            role: 'system',
            content: 'Switched to offline mode due to connection issues. Some features may be limited.'
          }]);
        }
      } else {
        setChatHistory(prev => [...prev, {
          role: 'system',
          content: `Error processing command: ${err.message || 'Unknown error occurred'}`
        }]);
        
        setError({
          type: 'command_processing',
          message: 'Failed to process your command',
          details: err.message || 'An unknown error occurred',
          recoverable: true
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handler functions that use the refs - these are stable and won't change between renders
  const handleNewGame = useCallback(() => handleNewGameRef.current?.(), []);
  const handleUserInput = useCallback((input: string) => handleUserInputRef.current?.(input), []);
  const handleDismissError = useCallback(() => setError(undefined), []);

  // Fetch available commands when component mounts
  useEffect(() => {
    const fetchCommands = async () => {
      try {
        const commands = await gameApi.getAvailableCommands();
        setAvailableCommands(commands);
      } catch (err) {
        console.error("Failed to fetch available commands:", err);
        // Provide fallback commands if API fails
        setAvailableCommands({
          movement: ['north', 'south', 'east', 'west', 'up', 'down'],
          actions: ['look', 'take', 'drop', 'inventory', 'use', 'talk', 'help'],
          japanese_commands: ['見る', '取る', '置く', '持ち物', '使う', '話す', 'ヘルプ']
        });
      }
    };
    
    fetchCommands();
  }, []);

  // Effect to setup game state after world data is transformed
  useEffect(() => {
    if (!transformedWorldData || isWorldGenerated) return;
    
    console.log("Setting up game state with transformed world data");
    
    try {
      // Create initial player state
      const playerData: Player = {
        current_location: "start",
        inventory: [],
        learned_vocabulary: {},
        stats: { 
          moves: 0,
          quests_completed: 0,
          locations_visited: [],
          items_collected: 0,
          vocabulary_learned: 0,
          grammar_points_mastered: 0
        }
      };
      
      // Ensure the start location has connections by checking world data
      if (transformedWorldData.locations.start) {
        const startLocation = transformedWorldData.locations.start;
        
        // If the start location has no connections, create default ones
        if (!startLocation.connections || Object.keys(startLocation.connections).length === 0) {
          console.warn("Start location has no connections, adding defaults");
          
          // Default locations to connect to
          const defaultConnections = {
            north: "forest",
            east: "shop",
            west: "house",
            south: "river"
          };
          
          // Add connections to start location
          startLocation.connections = defaultConnections;
          
          // Create these locations if they don't exist
          Object.entries(defaultConnections).forEach(([direction, targetId]) => {
            if (!transformedWorldData.locations[targetId]) {
              console.log(`Creating missing location: ${targetId}`);
              const oppositeDirection = getOppositeDirection(direction);
              
              transformedWorldData.locations[targetId] = {
                id: targetId,
                name: targetId.charAt(0).toUpperCase() + targetId.slice(1),
                japanese_name: `${targetId}エリア`,
                description: `A ${targetId} area connected to the starting point.`,
                japanese_description: `開始地点につながる${targetId}エリアです。`,
                connections: {
                  [oppositeDirection]: "start"
                },
                characters: [],
                items: [],
                vocabulary: [],
                visited: false
              };
            } else if (!transformedWorldData.locations[targetId].connections) {
              // Ensure the target has connections
              transformedWorldData.locations[targetId].connections = {};
            }
            
            // Ensure bidirectional connections
            const targetLocation = transformedWorldData.locations[targetId];
            const oppositeDirection = getOppositeDirection(direction);
            targetLocation.connections[oppositeDirection] = "start";
          });
        }
      }
      
      // Helper function to get opposite direction
      function getOppositeDirection(direction: string): string {
        const opposites: {[key: string]: string} = {
          north: "south",
          south: "north",
          east: "west",
          west: "east",
          up: "down",
          down: "up",
          in: "out",
          out: "in"
        };
        return opposites[direction] || "south";  // Default to south if unknown
      }
      
      // Set the full game state
      const newGameState: GameState = {
        world: transformedWorldData,
        player: playerData,
        visited_locations: [],
        flags: {},
        metadata: { creation_time: new Date().toISOString() },
        quest_log: {
          active_quests: {},
          completed_quests: {},
          failed_quests: {},
          available_quests: {}
        }
      };
      
      // Update all state in one batch to avoid race conditions
      setGameState(newGameState);
      setIsWorldGenerated(true);
      setError(undefined);
      
      // Add welcome message with basic tips for new players
      setChatHistory([
        {
          role: 'system',
          content: 'Welcome to your Japanese adventure! Here are some tips to get started:'
        },
        {
          role: 'system',
          content: '• Type "look" to see your surroundings\n• Move with "north", "south", "east", "west"\n• Examine objects with "look [object]"\n• Talk to characters with "talk [character]"\n• Type "help" for more commands\n• Click "How to Play" for full instructions\n• Remember: You can use Japanese commands too!'
        }
      ]);
      
      // Process a 'look' command after a short delay to allow state to settle
      const timer = setTimeout(() => {
        try {
          console.log("Executing initial look command");
          // Direct API call to avoid circular dependencies with handleUserInput
          gameApi.processInput('look', newGameState, [{
            role: 'system',
            content: 'Welcome to your Japanese adventure! Here are some tips to get started:'
          }])
          .then(result => {
            console.log("Initial look command result received");
            // Only update if the component is still mounted
            setGameState(prevState => {
              if (!prevState) return result.game_state;
              // Make sure we don't override more recent state updates
              return prevState.metadata.creation_time === newGameState.metadata.creation_time
                ? result.game_state
                : prevState;
            });
            
            setChatHistory(prevHistory => {
              // Only update if we haven't changed the history since game creation
              return prevHistory.length === 2 ? result.chat_history : prevHistory;
            });
          })
          .catch(err => {
            console.error("Error processing initial look command:", err);
            // Add fallback description if we can't get a proper look
            setChatHistory(prev => [
              ...prev,
              { 
                role: 'system', 
                content: `You are at ${transformedWorldData.locations.start.name} (${transformedWorldData.locations.start.japanese_name}). ${transformedWorldData.locations.start.description}`
              }
            ]);
          });
        } catch (err) {
          console.error("Error setting up initial look command:", err);
        }
      }, 1000);
      
      return () => clearTimeout(timer);
    } catch (err) {
      console.error("Error initializing game state:", err);
      setError({
        type: 'world_generation',
        message: 'Error initializing game',
        details: 'Failed to create game state from world data',
        recoverable: true
      });
    }
  }, [transformedWorldData, isWorldGenerated]);

  // Handler for loading saved games
  const handleLoadGame = useCallback((loadedState: GameState, loadedHistory: ChatMessage[]) => {
    try {
      setGameState(loadedState);
      setChatHistory(loadedHistory);
      setIsWorldGenerated(true);
      setError(undefined); // Clear any errors when loading a game
    } catch (err: any) {
      console.error("Error loading game:", err);
      setError({
        type: 'save_load',
        message: 'Failed to load saved game',
        details: err.message || 'Unknown error occurred while loading your game',
        recoverable: true
      });
    }
  }, []);

  // Get the current location description to show help text
  const getCurrentLocationText = useCallback(() => {
    if (!gameState || !isWorldGenerated) {
      return "Type 'start' to begin your adventure.";
    }
    
    const currentLocId = gameState.player.current_location;
    const currentLoc = gameState.world.locations[currentLocId];
    
    if (!currentLoc) {
      return "You are in an unknown location.";
    }
    
    return `You are at: ${currentLoc.name}${currentLoc.japanese_name ? ` (${currentLoc.japanese_name})` : ''}`;
  }, [gameState, isWorldGenerated]);
  
  // Get command help text
  const getCommandHelpText = useCallback(() => {
    if (!availableCommands) return "";
    
    return `
      Movement: ${availableCommands.movement.join(', ')}
      Actions: ${availableCommands.actions.join(', ')}
    `.trim();
  }, [availableCommands]);

  return (
    <div className="game-container">
      {error && (
        <ErrorNotification error={error} onDismiss={() => setError(undefined)} />
      )}
      
      <div className="game-controls flex justify-between items-center mb-4 max-w-7xl mx-auto px-4">
        <div className="flex items-center gap-2">
          <Button onClick={() => handleNewGameRef.current()} disabled={isLoading}>
            New Game
          </Button>
          <Button 
            onClick={() => setIsProfileOpen(true)} 
            disabled={!gameState}
            variant="outline"
          >
            Player Profile
          </Button>
          <Button 
            onClick={() => setIsInstructionsOpen(true)}
            variant="outline"
          >
            How to Play
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <SaveLoadControls 
            gameState={gameState} 
            chatHistory={chatHistory}
            onLoad={handleLoadGame}
            isWorldGenerated={isWorldGenerated}
            isLoading={isLoading}
          />
          {gameState && isWorldGenerated && (
            <Button 
              onClick={() => setIsMapVisible(!isMapVisible)}
              variant={isMapVisible ? "primary" : "outline"}
              className="ml-2"
            >
              {isMapVisible ? "Hide Map" : "Show Map"}
            </Button>
          )}
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-4 max-w-7xl mx-auto px-4">
        <div className={`game-content ${isMapVisible ? "lg:w-3/4" : "w-full"}`}>
          <div className="chat-container bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-md max-h-[80vh] overflow-hidden flex flex-col">
            <ChatHistory messages={chatHistory} />
            <div className="chat-input-container p-4 border-t border-gray-200 dark:border-gray-800 mt-auto">
              <div className="flex items-center gap-2">
                <ChatInput 
                  onSubmit={handleUserInputRef.current}
                  isLoading={isLoading || isValidating}
                  placeholder={isWorldGenerated ? "Enter a command like 'look' or '見る'..." : "Type 'start' to begin your adventure"}
                  suggestions={availableCommands?.japanese_commands}
                  error={error?.message}
                />
                {isLoading && (
                  <div className="flex-none flex items-center text-sm text-blue-600 dark:text-blue-400">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Processing...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
            <details>
              <summary className="cursor-pointer hover:text-gray-400">Available Commands</summary>
              <pre className="mt-1 p-2 bg-gray-900 rounded overflow-x-auto">
                {getCommandHelpText()}
              </pre>
            </details>
          </div>
        </div>
        
        {/* World Map Section - Shown on the right side when toggled */}
        {gameState && isWorldGenerated && isMapVisible && (
          <div className="map-container lg:w-1/4">
            <WorldMap
              worldData={gameState.world}
              currentLocation={gameState.player.current_location}
              visitedLocations={Array.from(gameState.visited_locations)}
              className="h-full"
            />
          </div>
        )}
      </div>

      {gameState && isProfileOpen && (
        <PlayerProfile
          gameState={gameState}
          isOpen={isProfileOpen}
          onClose={() => setIsProfileOpen(false)}
        />
      )}

      <GameInstructions
        isOpen={isInstructionsOpen}
        onClose={() => setIsInstructionsOpen(false)}
      />
    </div>
  );
};

export default GameContainer; 