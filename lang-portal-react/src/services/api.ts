import { API_BASE_URL } from '@/config/api';

export const api = {
  async generateVocabulary(theme: string) {
    const response = await fetch(`${API_BASE_URL}/generate-vocabulary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ theme })
    });

    if (!response.ok) {
      const errorText = await response.text();
      try {
        const errorJson = JSON.parse(errorText);
        throw new Error(errorJson.error || 'Failed to generate vocabulary');
      } catch {
        throw new Error(errorText || 'Failed to generate vocabulary');
      }
    }

    const text = await response.text();
    try {
      return JSON.parse(text);
    } catch {
      throw new Error('Invalid JSON response from server');
    }
  }
}; 