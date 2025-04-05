import { useState, useEffect } from 'react';
import { GameState, QuestObjective, Quest } from '../services/api';

interface GrammarChallengeProps {
  gameState: GameState;
  onSubmit: (answer: string) => void;
}

const GrammarChallenge: React.FC<GrammarChallengeProps> = ({ gameState, onSubmit }) => {
  const [answer, setAnswer] = useState('');
  const [currentChallenge, setCurrentChallenge] = useState<QuestObjective | null>(null);
  const [currentQuest, setCurrentQuest] = useState<Quest | null>(null);

  useEffect(() => {
    // Find the current active challenge when gameState changes
    if (gameState.active_grammar_challenge) {
      const { quest_id, objective_id } = gameState.active_grammar_challenge;
      const quest = gameState.quest_log.active_quests[quest_id];
      
      if (quest) {
        setCurrentQuest(quest);
        const objective = quest.objectives.find(obj => obj.id === objective_id) || null;
        setCurrentChallenge(objective);
      }
    } else {
      setCurrentChallenge(null);
      setCurrentQuest(null);
    }
  }, [gameState]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (answer.trim()) {
      onSubmit(answer);
      setAnswer('');
    }
  };

  if (!currentChallenge || !currentQuest) {
    return null;
  }

  const prompt = currentChallenge.properties?.prompt || 'Complete the grammar challenge';

  return (
    <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md border border-gray-300 dark:border-gray-700 mb-4">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-primary mb-1">
          Grammar Challenge: {currentChallenge.description}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {currentChallenge.japanese_description}
        </p>
      </div>
      
      <div className="mb-4 p-3 bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-600">
        <p className="font-medium">{prompt}</p>
      </div>
      
      <form onSubmit={handleSubmit} className="flex flex-col space-y-2">
        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Type your answer here..."
          className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
        />
        <button 
          type="submit" 
          className="bg-primary text-white py-2 px-4 rounded hover:bg-primary-dark transition-colors"
        >
          Submit Answer
        </button>
      </form>
      
      {currentChallenge.vocabulary && currentChallenge.vocabulary.length > 0 && (
        <div className="mt-4">
          <h4 className="font-bold text-sm mb-1">Vocabulary:</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {currentChallenge.vocabulary.map((vocab, idx) => (
              <div key={idx} className="p-2 bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-600">
                <div className="font-bold">{vocab.japanese}</div>
                <div>{vocab.english}</div>
                {vocab.reading && <div className="text-gray-500 dark:text-gray-400">{vocab.reading}</div>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GrammarChallenge; 