from TTS.api import TTS

# List available models
models = TTS().list_models()
print("Available TTS models:")
for model in models:
    print(f" - {model}")

# Try to load the Japanese models we're using
try:
    male_model = TTS(model_name="tts_models/ja/kokoro/tacotron2-DDC")
    print("Male Japanese model loaded successfully")
except Exception as e:
    print(f"Error loading male Japanese model: {str(e)}")

try:
    female_model = TTS(model_name="tts_models/ja/jsut/tacotron2-DDC")
    print("Female Japanese model loaded successfully")
except Exception as e:
    print(f"Error loading female Japanese model: {str(e)}") 