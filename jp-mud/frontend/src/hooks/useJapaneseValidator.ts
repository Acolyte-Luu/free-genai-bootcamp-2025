import { useState } from 'react';
import { gameApi } from '../services/api';

export const useJapaneseValidator = () => {
  const [isValidating, setIsValidating] = useState(false);

  const validateJapanese = async (text: string) => {
    setIsValidating(true);
    try {
      const result = await gameApi.validateJapanese(text);
      return result;
    } catch (error) {
      console.error('Error validating Japanese:', error);
      return { 
        is_valid: false, 
        feedback: 'Error validating text. Please try again.' 
      };
    } finally {
      setIsValidating(false);
    }
  };

  return {
    validateJapanese,
    isValidating
  };
}; 