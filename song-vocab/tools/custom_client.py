from typing import Any, Dict, Type, TypeVar
from pydantic import BaseModel
from ollama import Client
import json
import re
from tools.helper import fix_vocabulary_format

T = TypeVar('T', bound=BaseModel)

class CustomOllamaClient:
    """A custom client that works with instructor models but uses Ollama."""
    
    def __init__(self, host="http://localhost:9000"):
        print(f"Initializing Ollama client with host: {host}")
        try:
            self.client = Client(host=host)
            models = self.client.list()
            print(f"Successfully connected to Ollama. Available models: {[m['name'] for m in models['models']]}")
        except Exception as e:
            print(f"Failed to connect to Ollama: {e}")
            self.client = Client(host=host)  # Still create the client for later use
        
    def generate_structured(self, prompt: str, model: str, response_model: Type[T], **kwargs) -> T:
        """Generate a structured response using Ollama and parse with Pydantic."""
        # Define default options for Ollama - removing 'system' which is not supported
        options = {
            'temperature': 0.1,  # Low temperature for more precise structured responses
        }
        
        # Fix the schema issue by modifying how we present the schema
        schema = response_model.model_json_schema()
        schema_str = json.dumps(schema, indent=2)
        
        # Create a simplified schema without $defs section for the prompt
        simplified_schema = dict(schema)
        if "$defs" in simplified_schema:
            del simplified_schema["$defs"]
        
        # Include system instructions in the prompt itself
        system_instruction = "You are an assistant that responds in JSON format. Follow these rules exactly:"
        
        # Clean up the prompt to help with structured output
        structured_prompt = f"""
{system_instruction}

1. Your response must be a valid JSON object
2. Do not include the schema or any explanations in your response
3. Do not use markdown formatting like ```json or ``` in your response
4. Only return the JSON data that matches the structure specified

{prompt}

EXPECTED JSON STRUCTURE:
{json.dumps(simplified_schema, indent=2)}

EXAMPLE VALID RESPONSE:
{{
  "action": {{
    "tool": "search_web",
    "tool_input": {{
      "query": "example search"
    }},
    "thought": "I need to search for information"
  }}
}}

OR 

{{
  "final_answer": {{
    "lyrics": "Song lyrics here...",
    "vocabulary": [
      {{
        "kanji": "例",
        "romaji": "rei",
        "english": "example",
        "parts": [
          {{
            "kanji": "例",
            "romaji": ["rei"]
          }}
        ]
      }}
    ]
  }}
}}

Response (JSON only):
"""
        
        print(f"Sending request to Ollama: model={model}, temperature={options['temperature']}")
        
        # Call Ollama with the allowed options
        response = self.client.generate(
            model=model,
            prompt=structured_prompt,
            options=options
        )
        
        # Parse the response text with the provided Pydantic model
        try:
            # Get the response text
            text = response.get('response', '')
            print(f"Received response from Ollama: {text[:100]}...")
            
            # Filter out schema definitions if they appear in the response
            text = re.sub(r'\{\s*"\$defs":.+?\}\s*', '', text)
            
            # Try to clean up the text if it's not pure JSON (remove markdown code blocks, etc.)
            text = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', text)
            
            # Clean up any remaining non-JSON text
            match = re.search(r'(\{[\s\S]*\})', text)
            if match:
                text = match.group(1)
                print("Extracted JSON from text")
            
            print(f"Cleaned JSON: {text[:100]}...")
            
            # Parse with Pydantic model
            try:
                # Try direct JSON parsing first
                parsed = response_model.model_validate_json(text)
                print(f"Successfully parsed JSON response as {response_model.__name__}")
                
                # Fix vocabulary format if this is an AgentResponse
                if response_model.__name__ == "AgentResponse":
                    parsed_dict = parsed.model_dump()
                    fixed_dict = fix_vocabulary_format(parsed_dict)
                    parsed = response_model.model_validate(fixed_dict)
                
                return parsed
            except Exception as json_error:
                # If that fails, try to interpret the response and create a model
                print(f"JSON parsing failed: {json_error}")
                print(f"Attempting fallback parsing for text: {text[:200]}...")
                
                # Try to extract JSON using more aggressive pattern matching
                potential_json = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
                if potential_json:
                    try:
                        json_text = potential_json.group(1)
                        print(f"Found potential JSON: {json_text[:100]}...")
                        data = json.loads(json_text)
                        if response_model.__name__ == "AgentResponse":
                            data = fix_vocabulary_format(data)
                        parsed = response_model.model_validate(data)
                        print("Successfully parsed JSON using pattern matching")
                        return parsed
                    except Exception as e:
                        print(f"Pattern matching JSON parsing failed: {e}")
                
                # Last resort: try to build the model directly from the text directly
                print("Attempting to create model directly from text")
                return response_model(text=text)
        except Exception as e:
            print(f"Final error in generate_structured: {e}")
            raise ValueError(f"Failed to parse response: {e}") 