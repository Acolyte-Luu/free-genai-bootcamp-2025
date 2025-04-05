# Create BedrockChat
# bedrock_chat.py
import requests
import streamlit as st
from typing import Optional, Dict, Any
import json


# Model ID
# MODEL_ID = "amazon.nova-micro-v1:0"
MODEL_ID = "qwen2.5:7b"


class LocalLLMChat:
    def __init__(self, api_url: str = "http://localhost:9000/api/chat"):
        """Initialize Local LLM chat client
        
        Args:
            api_url: The URL of your Ollama API endpoint
        """
        self.api_url = api_url

    def generate_response(self, message: str, inference_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate a response using Ollama"""
        if inference_config is None:
            inference_config = {"temperature": 0.7}

        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "user", "content": message}
            ],
            "stream": False,  # Set to False to get complete response
            **inference_config
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            # Get the last message from the response that contains content
            response_data = response.json()
            if isinstance(response_data, dict) and 'message' in response_data:
                return response_data['message']['content']
            
            # If we got a list of responses (streaming), concatenate them
            full_response = ""
            for line in response.text.strip().split('\n'):
                try:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        full_response += data['message']['content']
                except json.JSONDecodeError:
                    continue
            
            return full_response.strip()
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            print(f"Error: {str(e)}")  # Add this for debugging
            return None


if __name__ == "__main__":
    chat = LocalLLMChat()
    while True:
        user_input = input("You: ")
        if user_input.lower() == '/exit':
            break
        response = chat.generate_response(user_input)
        print("Bot:", response)
