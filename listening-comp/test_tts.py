from TTS.api import TTS
import os

# Set up directories
os.makedirs("/app/data", exist_ok=True)

# Simple test
print("Testing TTS functionality...")
text = "こんにちは"
output_file = "/app/data/test_output.wav"

# List available models
print("Available models:")
tts = TTS()
# Get models list using the correct API method
try:
    # Different ways to access models based on TTS version
    if hasattr(tts, 'list_models'):
        models = tts.list_models()
        if hasattr(models, 'list_models'):
            # New API - models is a ModelManager
            japanese_models = [m for m in models.list_models() if "ja" in m]
        else:
            # Old API - models is already a list
            japanese_models = [m for m in models if "ja" in m]
    else:
        japanese_models = []
        print("Couldn't access model list")
        
    for model in japanese_models:
        print(f" - {model}")
except Exception as e:
    print(f"Error listing models: {str(e)}")
    import traceback
    traceback.print_exc()

# Try the model
model_name = "tts_models/ja/kokoro/tacotron2-DDC"
print(f"Loading model: {model_name}")
try:
    tts = TTS(model_name=model_name)
    print("Model loaded successfully")
    
    print(f"Generating speech for text: {text}")
    tts.tts_to_file(text=text, file_path=output_file)
    
    print(f"Speech generated successfully: {output_file}")
    print(f"File exists: {os.path.exists(output_file)}")
    print(f"File size: {os.path.getsize(output_file) if os.path.exists(output_file) else 'N/A'}")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc() 