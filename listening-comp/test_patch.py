#!/usr/bin/env python3

# Explicitly apply the patch before anything else
exec(open("/app/pytorch_patch.py").read())

import sys
print(f"Python version: {sys.version}")

# Verify our patch is applied
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"Is torch.load patched: {torch.load.__name__ == 'patched_load'}")

# Now test TTS with a simple example
try:
    from TTS.api import TTS
    print("Successfully imported TTS")
    
    # Initialize TTS with a Japanese model
    model_name = "tts_models/ja/kokoro/tacotron2-DDC"
    print(f"Loading model: {model_name}")
    tts = TTS(model_name=model_name)
    print("Model loaded successfully!")
    
    # Generate a simple test file
    text = "こんにちは、世界"
    output_file = "/app/data/patch_test.wav"
    print(f"Generating speech for: '{text}'")
    tts.tts_to_file(text=text, file_path=output_file)
    
    # Verify the file was created
    import os
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"Success! Audio file created: {output_file} ({size} bytes)")
    else:
        print(f"Error: Output file not created")
    
except Exception as e:
    print(f"Error during TTS test: {e}")
    import traceback
    traceback.print_exc() 