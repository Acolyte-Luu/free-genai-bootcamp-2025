# LocalLLM wrapper module for writing practice app
import requests
import json

# Use the same model as in your chat.py
MODEL_ID = "llama3.1:8b"

class LocalLLM:
    """
    Wrapper class for local LLM interaction using Ollama API.
    Adapted to work with the existing Ollama instance.
    """
    
    def __init__(self, api_url="http://localhost:9000/api/chat"):
        """Initialize the LLM wrapper to use your Ollama API"""
        self.api_url = api_url
        self.model = MODEL_ID
        print(f"Initializing LocalLLM wrapper for {self.model}")
    
    def generate(self, prompt):
        """
        Generate text based on the input prompt
        
        Args:
            prompt (str): The input prompt/instructions
            
        Returns:
            str: The generated text response
        """
        print(f"Generating response for prompt: {prompt[:50]}...")
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            if isinstance(response_data, dict) and 'message' in response_data:
                return response_data['message']['content']
            
            # Handle streaming responses (just in case)
            full_response = ""
            for line in response.text.strip().split('\n'):
                try:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        full_response += data['message']['content']
                except json.JSONDecodeError:
                    continue
            
            return full_response.strip() or "No response generated"
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            # Return fallback responses to keep the app functional during errors
            if "sentence" in prompt:
                return "I eat sushi every day."
            elif "translation" in prompt:
                return "I study Japanese."
            elif "Grade this" in prompt:
                return "Grade: B\nFeedback: Could not generate proper feedback due to API error."
            else:
                return f"Error: {str(e)}" 