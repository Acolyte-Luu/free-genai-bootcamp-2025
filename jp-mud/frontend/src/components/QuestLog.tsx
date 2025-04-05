import { useState } from 'react';
import { GameState, Quest } from '../services/api';

interface QuestLogProps {
  gameState: GameState | undefined;
  isOpen: boolean;
  onClose: () => void;
}

const QuestLog = ({ gameState, isOpen, onClose }: QuestLogProps) => {
  const [selectedQuestId, setSelectedQuestId] = useState<string | null>(null);

  if (!isOpen) return null;

  // Exit early if no game state or quests
  if (!gameState || !gameState.quest_log) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-card dark:bg-card-dark w-full max-w-lg mx-auto rounded-lg shadow-lg overflow-hidden">
          <div className="p-4 bg-primary text-white flex justify-between">
            <h2 className="text-lg font-bold">Quest Log</h2>
            <button onClick={onClose} className="text-white hover:text-gray-300">✕</button>
          </div>
          <div className="p-6">
            <p>No quests available yet. Explore the world to discover quests!</p>
          </div>
        </div>
      </div>
    );
  }

  const { active_quests = {}, available_quests = {}, completed_quests = {} } = gameState.quest_log;
  
  // Function to calculate quest progress
  const getQuestProgress = (quest: Quest) => {
    if (!quest.objectives || quest.objectives.length === 0) return 0;
    const completedObjectives = quest.objectives.filter(obj => obj.completed).length;
    return Math.round((completedObjectives / quest.objectives.length) * 100);
  };
  
  // Get the selected quest details
  const selectedQuest = selectedQuestId 
    ? active_quests[selectedQuestId] || available_quests[selectedQuestId] || completed_quests[selectedQuestId]
    : null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-card dark:bg-card-dark w-full max-w-4xl mx-auto rounded-lg shadow-lg overflow-hidden">
        <div className="p-4 bg-primary text-white flex justify-between">
          <h2 className="text-lg font-bold">Quest Log (クエスト記録)</h2>
          <button onClick={onClose} className="text-white hover:text-gray-300">✕</button>
        </div>
        <div className="grid grid-cols-12 h-[600px]">
          {/* Quest List Sidebar */}
          <div className="col-span-4 border-r border-gray-700 overflow-y-auto p-4">
            {Object.keys(active_quests).length > 0 && (
              <div className="mb-6">
                <h3 className="text-md font-semibold mb-2 text-primary">Active Quests (進行中)</h3>
                <ul className="space-y-2">
                  {Object.entries(active_quests).map(([id, quest]) => (
                    <li 
                      key={id}
                      className={`p-2 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition
                        ${selectedQuestId === id ? 'bg-gray-100 dark:bg-gray-800' : ''}`}
                      onClick={() => setSelectedQuestId(id)}
                    >
                      <div className="font-medium">{quest.title}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">{quest.japanese_title}</div>
                      <div className="mt-1 h-1 w-full bg-gray-300 dark:bg-gray-700 rounded">
                        <div 
                          className="h-full bg-secondary rounded"
                          style={{ width: `${getQuestProgress(quest)}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-right mt-1">
                        {getQuestProgress(quest)}%
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {Object.keys(available_quests).length > 0 && (
              <div className="mb-6">
                <h3 className="text-md font-semibold mb-2 text-primary">Available Quests (利用可能)</h3>
                <ul className="space-y-2">
                  {Object.entries(available_quests).map(([id, quest]) => (
                    <li 
                      key={id}
                      className={`p-2 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition
                        ${selectedQuestId === id ? 'bg-gray-100 dark:bg-gray-800' : ''}`}
                      onClick={() => setSelectedQuestId(id)}
                    >
                      <div className="font-medium">{quest.title}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">{quest.japanese_title}</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {Object.keys(completed_quests).length > 0 && (
              <div>
                <h3 className="text-md font-semibold mb-2 text-primary">Completed Quests (完了)</h3>
                <ul className="space-y-2">
                  {Object.entries(completed_quests).map(([id, quest]) => (
                    <li 
                      key={id}
                      className={`p-2 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition
                        ${selectedQuestId === id ? 'bg-gray-100 dark:bg-gray-800' : ''}`}
                      onClick={() => setSelectedQuestId(id)}
                    >
                      <div className="font-medium line-through">{quest.title}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">{quest.japanese_title}</div>
                      <div className="text-xs text-green-500">✓ Complete</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {Object.keys(active_quests).length === 0 && 
             Object.keys(available_quests).length === 0 &&
             Object.keys(completed_quests).length === 0 && (
              <p className="text-center py-8 text-gray-500">
                No quests available yet.<br />
                Explore the world to discover quests!
              </p>
            )}
          </div>
          
          {/* Quest Details */}
          <div className="col-span-8 p-6 overflow-y-auto">
            {selectedQuest ? (
              <div>
                <div className="mb-4">
                  <h2 className="text-xl font-bold">{selectedQuest.title}</h2>
                  <h3 className="text-lg font-medium text-gray-600 dark:text-gray-400">
                    {selectedQuest.japanese_title}
                  </h3>
                </div>
                
                <div className="mb-6">
                  <p>{selectedQuest.description}</p>
                  <p className="mt-2 text-gray-600 dark:text-gray-400">{selectedQuest.japanese_description}</p>
                </div>
                
                {selectedQuest.objectives && selectedQuest.objectives.length > 0 && (
                  <div className="mb-6">
                    <h4 className="font-bold mb-2">Objectives:</h4>
                    <ul className="space-y-3">
                      {selectedQuest.objectives.map((objective, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className={`mr-2 ${objective.completed ? 'text-green-500' : 'text-gray-400'}`}>
                            {objective.completed ? '✓' : '○'}
                          </span>
                          <div>
                            <div>{objective.description}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              {objective.japanese_description}
                            </div>
                            {objective.count > 1 && (
                              <div className="text-sm">
                                Progress: {objective.progress} / {objective.count}
                              </div>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {selectedQuest.rewards && selectedQuest.rewards.length > 0 && (
                  <div>
                    <h4 className="font-bold mb-2">Rewards:</h4>
                    <ul className="space-y-2">
                      {selectedQuest.rewards.map((reward, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className={`mr-2 ${reward.claimed ? 'text-green-500' : 'text-gray-400'}`}>
                            {reward.claimed ? '✓' : '•'}
                          </span>
                          <div>
                            <div>{reward.description}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              {reward.japanese_description}
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {selectedQuest.state === 'completed' && (
                  <div className="mt-6 p-2 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded">
                    Quest completed!
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Select a quest to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestLog; 