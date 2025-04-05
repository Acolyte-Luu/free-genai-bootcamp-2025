import { useState, KeyboardEvent, useRef, useEffect, useCallback } from 'react';
import { Button } from './ui/Button';

interface ChatInputProps {
  onSubmit: (input: string) => void;
  isLoading: boolean;
  error?: string;
  placeholder?: string;
  suggestions?: string[];
}

const ChatInput = ({ 
  onSubmit, 
  isLoading, 
  error, 
  placeholder = "Enter your command...",
  suggestions = []
}: ChatInputProps) => {
  const [input, setInput] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  
  // Memoized filter function to prevent unnecessary filtering
  const filterSuggestions = useCallback(() => {
    if (suggestions.length > 0 && input) {
      const filtered = suggestions.filter(suggestion =>
        suggestion.toLowerCase().includes(input.toLowerCase())
      );
      return filtered.slice(0, 5); // Limit to 5 suggestions
    }
    return [];
  }, [input, suggestions]);

  // Focus input on mount and when loading state changes
  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  // Handle outside clicks to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current && 
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Filter suggestions when input changes
  useEffect(() => {
    setFilteredSuggestions(filterSuggestions());
  }, [filterSuggestions]);

  const handleSubmit = () => {
    if (input.trim() && !isLoading) {
      onSubmit(input.trim());
      setInput('');
      setShowSuggestions(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    } else if (showSuggestions && filteredSuggestions.length > 0) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        // Not implementing suggestion navigation with arrows for simplicity
        // but you could add this feature later
      }
    }
  };

  const handleSuggestionClick = useCallback((suggestion: string) => {
    setInput(suggestion);
    setShowSuggestions(false);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
    if (suggestions.length > 0) {
      setShowSuggestions(true);
    }
  }, [suggestions]);

  const handleInputFocus = useCallback(() => {
    if (input && suggestions.length > 0 && filteredSuggestions.length > 0) {
      setShowSuggestions(true);
    }
  }, [input, suggestions, filteredSuggestions]);

  return (
    <div className="w-full">
      <label htmlFor="command-input" className="sr-only">
        Enter your command
      </label>
      <div className="flex items-center space-x-2">
        <div className="relative flex-1">
          <input
            id="command-input"
            ref={inputRef}
            type="text"
            value={input}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="w-full h-10 px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
            aria-disabled={isLoading}
            aria-describedby={error ? "input-error" : undefined}
          />
          
          {/* Suggestions dropdown */}
          {showSuggestions && filteredSuggestions.length > 0 && (
            <div 
              ref={suggestionsRef}
              className="absolute z-10 w-full mt-1 bg-background border border-input rounded-md shadow-lg max-h-60 overflow-auto"
            >
              <ul className="py-1">
                {filteredSuggestions.map((suggestion, index) => (
                  <li
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="px-3 py-2 hover:bg-accent cursor-pointer"
                  >
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <Button
          onClick={handleSubmit}
          disabled={isLoading || !input.trim()}
          className="h-10"
          aria-label="Send command"
        >
          {isLoading ? (
            <span 
              className="inline-block h-4 w-4 border-2 border-t-transparent border-white rounded-full animate-spin" 
              aria-hidden="true"
            />
          ) : (
            'Send'
          )}
        </Button>
      </div>
      {error && (
        <p 
          id="input-error" 
          className="text-red-500 mt-2" 
          role="alert"
          aria-live="assertive"
        >
          {error}
        </p>
      )}
    </div>
  );
};

export default ChatInput; 