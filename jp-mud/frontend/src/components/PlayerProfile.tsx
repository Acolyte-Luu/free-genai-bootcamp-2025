import { GameState } from '../services/api';

interface PlayerProfileProps {
  gameState: GameState;
  isOpen: boolean;
  onClose: () => void;
}

const PlayerProfile: React.FC<PlayerProfileProps> = ({ gameState, isOpen, onClose }) => {
  if (!isOpen) return null;
  
  const { player } = gameState;
  const jlptLevels = [5, 4, 3, 2, 1];
  
  // Get JLPT progress
  const getJlptProgress = (level: number): number => {
    return player.stats.jlpt_progress?.[level] || 0;
  };
  
  // Calculate vocabulary mastery percentage
  const vocabMasteryPercentage = () => {
    const totalVocab = Object.keys(gameState.world.vocabulary).length;
    if (totalVocab === 0) return 0;
    return Math.round((player.stats.vocabulary_learned / totalVocab) * 100);
  };

  // Format time played
  const formatTimePlayed = () => {
    const seconds = player.stats.time_played;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  };

  // Get recently learned grammar points
  const getRecentGrammarPoints = () => {
    const grammarPoints = player.knowledge?.grammar_points || [];
    return grammarPoints.slice(-5).reverse(); // Get last 5, most recent first
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-card dark:bg-card-dark w-full max-w-2xl mx-auto rounded-lg shadow-lg overflow-hidden">
        <div className="p-4 bg-primary text-white flex justify-between">
          <h2 className="text-lg font-bold">Player Profile</h2>
          <button onClick={onClose} className="text-white hover:text-gray-300">✕</button>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[80vh]">
          {/* JLPT Level */}
          <div className="mb-6">
            <h3 className="text-xl font-bold mb-2">JLPT Level: N{player.jlpt_level}</h3>
            <div className="grid grid-cols-5 gap-2">
              {jlptLevels.map(level => (
                <div key={level} className="text-center">
                  <div className={`rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-1 ${level === player.jlpt_level ? 'bg-primary text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>
                    N{level}
                  </div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-secondary" 
                      style={{ width: `${getJlptProgress(level)}%` }}
                    ></div>
                  </div>
                  <span className="text-xs">{getJlptProgress(level)}%</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Stats */}
          <div className="mb-6">
            <h3 className="font-bold mb-2">Game Progress</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded">
                <div className="font-medium">Quests Completed</div>
                <div className="text-2xl">{player.stats.quests_completed}</div>
              </div>
              <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded">
                <div className="font-medium">Locations Discovered</div>
                <div className="text-2xl">{player.stats.locations_visited.size || 0}</div>
              </div>
              <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded">
                <div className="font-medium">Items Collected</div>
                <div className="text-2xl">{player.stats.items_collected}</div>
              </div>
              <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded">
                <div className="font-medium">Moves Made</div>
                <div className="text-2xl">{player.stats.moves}</div>
              </div>
            </div>
          </div>
          
          {/* Language Progress */}
          <div className="mb-6">
            <h3 className="font-bold mb-2">Language Progress</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded">
                <div className="font-medium">Vocabulary Learned</div>
                <div className="text-2xl">{player.stats.vocabulary_learned}</div>
                <div className="text-sm text-gray-500">
                  {vocabMasteryPercentage()}% of total
                </div>
              </div>
              <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded">
                <div className="font-medium">Grammar Points</div>
                <div className="text-2xl">{player.stats.grammar_points_mastered}</div>
              </div>
            </div>
          </div>
          
          {/* Recent Grammar Points */}
          <div className="mb-4">
            <h3 className="font-bold mb-2">Recently Learned Grammar</h3>
            {getRecentGrammarPoints().length > 0 ? (
              <ul className="space-y-2">
                {getRecentGrammarPoints().map((grammar, idx) => (
                  <li key={idx} className="p-3 bg-gray-100 dark:bg-gray-800 rounded">
                    <div className="font-medium">{grammar.name}</div>
                    <div className="text-sm mt-1">{grammar.explanation}</div>
                    {grammar.examples && grammar.examples.length > 0 && (
                      <div className="mt-2 text-sm">
                        <div className="font-medium">Examples:</div>
                        <ul className="space-y-1 mt-1">
                          {grammar.examples.map((ex, i) => (
                            <li key={i}>
                              <div className="font-mono">{ex.japanese}</div>
                              <div className="text-gray-500 dark:text-gray-400">{ex.english}</div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500">No grammar points learned yet.</p>
            )}
          </div>
          
          {/* Play Time */}
          <div className="text-sm text-gray-500 text-right">
            Time played: {formatTimePlayed()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayerProfile; 