import React from 'react';
import { Button } from './ui/Button';
import { X } from 'lucide-react';

interface GameInstructionsProps {
  isOpen: boolean;
  onClose: () => void;
}

const GameInstructions: React.FC<GameInstructionsProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
        <div className="flex justify-between items-center sticky top-0 bg-white dark:bg-gray-800 p-4 border-b">
          <h2 className="text-xl font-bold">Game Instructions</h2>
          <Button variant="outline" size="sm" onClick={onClose} aria-label="Close">
            <X className="h-5 w-5" />
          </Button>
        </div>
        
        <div className="p-6 space-y-6">
          <section className="space-y-2">
            <h3 className="text-lg font-semibold">Getting Started</h3>
            <p>JP-MUD is a text-based adventure game that combines exploration with Japanese language learning. You'll navigate a virtual world, interact with characters, collect items, and complete quests while learning Japanese vocabulary and grammar.</p>
            
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-md">
              <p className="font-medium">To start a new game:</p>
              <ul className="list-disc pl-6 mt-2">
                <li>Click the "New Game" button or type <code>start</code> in the command input</li>
                <li>Wait for the world to generate</li>
                <li>Begin exploring with commands like <code>look</code></li>
              </ul>
            </div>
          </section>
          
          <section className="space-y-2">
            <h3 className="text-lg font-semibold">Basic Commands</h3>
            <p>You'll interact with the game world by typing commands. Here are the essential commands:</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-md">
                <p className="font-medium">Movement:</p>
                <ul className="list-disc pl-6 mt-2">
                  <li><code>north</code>, <code>south</code>, <code>east</code>, <code>west</code> (or <code>n</code>, <code>s</code>, <code>e</code>, <code>w</code>)</li>
                  <li><code>up</code>, <code>down</code> (or <code>u</code>, <code>d</code>)</li>
                  <li><code>in</code>, <code>out</code></li>
                  <li>Japanese: <code>北</code>, <code>南</code>, <code>東</code>, <code>西</code>, <code>上</code>, <code>下</code></li>
                </ul>
              </div>
              
              <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-md">
                <p className="font-medium">Looking Around:</p>
                <ul className="list-disc pl-6 mt-2">
                  <li><code>look</code> - View your current location</li>
                  <li><code>look [object/character]</code> - Examine something specific</li>
                  <li>Japanese: <code>見る</code>, <code>調べる</code></li>
                </ul>
              </div>
              
              <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-md">
                <p className="font-medium">Items:</p>
                <ul className="list-disc pl-6 mt-2">
                  <li><code>take [item]</code> - Pick up an item</li>
                  <li><code>drop [item]</code> - Drop an item</li>
                  <li><code>inventory</code> (or <code>i</code>) - Check what you're carrying</li>
                  <li><code>use [item]</code> - Use an item you're carrying</li>
                  <li>Japanese: <code>取る</code>, <code>置く</code>, <code>持ち物</code>, <code>使う</code></li>
                </ul>
              </div>
              
              <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-md">
                <p className="font-medium">Interaction:</p>
                <ul className="list-disc pl-6 mt-2">
                  <li><code>talk [character]</code> - Talk to a character</li>
                  <li><code>help</code> - Show commands list</li>
                  <li>Japanese: <code>話す</code>, <code>聞く</code>, <code>ヘルプ</code></li>
                </ul>
              </div>
            </div>
          </section>
          
          <section className="space-y-2">
            <h3 className="text-lg font-semibold">Quests & Language Learning</h3>
            <p>The game features quests that help you practice Japanese while progressing through the story.</p>
            
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-md">
              <p className="font-medium">Quest Commands:</p>
              <ul className="list-disc pl-6 mt-2">
                <li><code>quests</code> - View your active quests</li>
                <li><code>grammar [challenge_id]</code> - Start a grammar challenge</li>
                <li>Japanese: <code>クエスト</code>, <code>文法</code></li>
              </ul>
            </div>
            
            <p className="mt-4">As you explore, you'll discover new vocabulary attached to locations, characters, and items. These will be added to your vocabulary list in your profile. Try to use Japanese commands when possible to practice!</p>
            
            <div className="bg-yellow-100 dark:bg-yellow-900 p-4 rounded-md text-yellow-800 dark:text-yellow-200">
              <p className="font-medium">Language Features:</p>
              <ul className="list-disc pl-6 mt-2">
                <li><strong>Japanese Input:</strong> You can type commands in either English or Japanese</li>
                <li><strong>Validation:</strong> When you use Japanese, the system checks if it's correct</li>
                <li><strong>Vocabulary:</strong> Each location, character, and item teaches new words</li>
                <li><strong>Grammar Challenges:</strong> Complete these to improve your Japanese skills</li>
              </ul>
            </div>
          </section>
          
          <section className="space-y-2">
            <h3 className="text-lg font-semibold">Game Controls</h3>
            <p>The game interface provides several control options:</p>
            
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-md">
              <ul className="list-disc pl-6">
                <li><strong>New Game:</strong> Start a fresh adventure</li>
                <li><strong>Profile:</strong> View your player stats and learned vocabulary</li>
                <li><strong>Save/Load:</strong> Save your progress or load a previous game</li>
                <li><strong>Command Input:</strong> Type your commands at the bottom of the screen</li>
              </ul>
            </div>
          </section>
          
          <section className="space-y-2">
            <h3 className="text-lg font-semibold">Tips for Success</h3>
            <ul className="list-disc pl-6">
              <li>Explore thoroughly - check all directions and examine objects</li>
              <li>Talk to characters multiple times - they may have different dialogue options</li>
              <li>Collect items as you find them - they might be useful later</li>
              <li>Use the "look" command frequently to understand your surroundings</li>
              <li>Try using Japanese commands to practice what you're learning</li>
              <li>Save your game regularly to preserve your progress</li>
            </ul>
          </section>
        </div>
        
        <div className="border-t p-4 flex justify-end">
          <Button onClick={onClose}>Close Instructions</Button>
        </div>
      </div>
    </div>
  );
};

export default GameInstructions; 