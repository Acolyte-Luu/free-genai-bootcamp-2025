import { useEffect, useRef } from 'react';
import { ChatMessage } from '../services/api';

interface ChatHistoryProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

const ChatHistory = ({ messages, isLoading = false }: ChatHistoryProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Format system messages that contain bullet points
  const formatSystemMessage = (content: string) => {
    const lines = content.split('\n');
    return lines.map((line, i) => {
      if (line.startsWith('•') || line.startsWith('-')) {
        return (
          <div key={i} className="flex items-start my-1">
            <span className="flex-shrink-0 mr-2">{line.charAt(0)}</span>
            <span>{line.substring(1).trim()}</span>
          </div>
        );
      }
      return <p key={i} className="my-1">{line}</p>;
    });
  };

  return (
    <div className="flex flex-col w-full h-full overflow-y-auto p-4 space-y-4 terminal">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          } ${index === 0 ? 'mt-auto' : ''}`}
        >
          <div
            className={`
              ${message.role === 'user'
                ? 'message-user bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                : message.role === 'assistant'
                ? 'message-assistant bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 w-full'}
              rounded-lg p-3 shadow-sm
            `}
          >
            {
              message.role === 'system'
              ? <div className="text-sm" style={{ whiteSpace: 'pre-wrap' }}>{formatSystemMessage(message.content)}</div>
              : <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
            }
          </div>
        </div>
      ))}
      
      {isLoading && (
        <div className="flex justify-start">
          <div className="message-assistant bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-gray-400 dark:bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 dark:bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 dark:bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatHistory; 