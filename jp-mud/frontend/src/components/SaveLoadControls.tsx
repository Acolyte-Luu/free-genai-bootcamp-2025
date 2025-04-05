import { useState } from 'react';
import { GameState, ChatMessage, gameApi } from '../services/api';
import { Button } from './ui/Button';

interface SavedGame {
  game_id: string;
  timestamp: string;
  location: string;
  player_stats: Record<string, any>;
}

interface SaveLoadControlsProps {
  gameState: GameState | undefined;
  chatHistory: ChatMessage[];
  onLoad: (gameState: GameState, chatHistory: ChatMessage[]) => void;
  isWorldGenerated: boolean;
  isLoading: boolean;
}

const SaveLoadControls: React.FC<SaveLoadControlsProps> = ({
  gameState, 
  chatHistory, 
  onLoad, 
  isWorldGenerated, 
  isLoading
}) => {
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadMenuOpen, setIsLoadMenuOpen] = useState(false);
  const [savedGames, setSavedGames] = useState<SavedGame[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const handleSaveGame = async () => {
    if (!gameState) return;
    
    setIsSaving(true);
    setSaveSuccess(null);
    
    try {
      const result = await gameApi.saveGameState(gameState, chatHistory);
      if (result.status === 'success') {
        setSaveSuccess(`Game saved! ID: ${result.game_id?.substring(0, 8)}...`);
        
        // Auto-hide success message after 3 seconds
        setTimeout(() => {
          setSaveSuccess(null);
        }, 3000);
      }
    } catch (error) {
      console.error('Error saving game:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleOpenLoadMenu = async () => {
    setIsLoadMenuOpen(true);
    setLoadError(null);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/saved-games`);
      if (!response.ok) throw new Error('Failed to fetch saved games');
      
      const data = await response.json();
      setSavedGames(data.saved_games || []);
    } catch (error) {
      console.error('Error fetching saved games:', error);
      setLoadError('Failed to fetch saved games');
    }
  };

  const handleLoadGame = async (gameId: string) => {
    setLoadError(null);
    
    try {
      const result = await gameApi.loadGameState(gameId);
      onLoad(result.state as unknown as GameState, result.chat_history);
      setIsLoadMenuOpen(false);
    } catch (error) {
      console.error('Error loading game:', error);
      setLoadError('Failed to load game');
    }
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (e) {
      return 'Unknown date';
    }
  };

  return (
    <div className="relative">
      <div className="flex space-x-2">
        <Button
          onClick={handleSaveGame}
          disabled={isLoading || isSaving || !isWorldGenerated}
          aria-label="Save game"
          variant="secondary"
        >
          {isSaving ? 'Saving...' : 'Save'}
        </Button>
        
        <Button
          onClick={handleOpenLoadMenu}
          disabled={isLoading}
          aria-label="Load game"
          variant="secondary"
        >
          Load
        </Button>
      </div>
      
      {saveSuccess && (
        <div className="absolute right-0 mt-2 p-2 bg-green-100 text-green-800 rounded text-sm">
          {saveSuccess}
        </div>
      )}
      
      {isLoadMenuOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded shadow-lg z-10">
          <div className="p-2 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <h3 className="font-bold">Load Game</h3>
            <button 
              onClick={() => setIsLoadMenuOpen(false)}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>
          
          <div className="p-2 max-h-80 overflow-y-auto">
            {loadError && (
              <div className="text-red-500 text-sm mb-2">{loadError}</div>
            )}
            
            {savedGames.length === 0 ? (
              <div className="text-gray-500 text-sm py-4 text-center">
                No saved games found
              </div>
            ) : (
              <ul className="space-y-2">
                {savedGames.map(game => (
                  <li 
                    key={game.game_id}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded cursor-pointer transition"
                    onClick={() => handleLoadGame(game.game_id)}
                  >
                    <div className="font-medium text-sm">{game.location}</div>
                    <div className="text-xs text-gray-500">
                      {formatDate(game.timestamp)}
                    </div>
                    <div className="text-xs mt-1">
                      Quests: {game.player_stats.quests_completed || 0} | 
                      Moves: {game.player_stats.moves || 0}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SaveLoadControls; 