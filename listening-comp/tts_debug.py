#!/usr/bin/env python3

# Apply the patch first - this is critical
exec(open("/app/pytorch_patch.py").read())

import sys
import os
from TTS.api import TTS
import torch

def test_tts_functionality():
    """Test TTS functionality with the PyTorch patch"""
    print(f"PyTorch version: {torch.__version__}")
    print(f"Is torch.load patched: {torch.load.__name__ == 'patched_load'}")
    
    # Get available models
    print("\nListing available models:")
    tts_api = TTS()
    models = tts_api.list_models()
    
    # Get Japanese models
    japanese_models = []
    if hasattr(models, 'list_models'):
        japanese_models = [m for m in models.list_models() if "ja" in m]
    else:
        japanese_models = [m for m in models if "ja" in m]
        
    for model in japanese_models:
        print(f" - {model}")
    
    # Test with a specific model
    model_name = "tts_models/ja/kokoro/tacotron2-DDC"
    print(f"\nLoading model: {model_name}")
    try:
        tts = TTS(model_name=model_name)
        print("✓ Model loaded successfully")
        
        # Test TTS with different text lengths
        test_texts = [
            "こんにちは",  # Very short
            "今日はいい天気ですね",  # Medium
            "この文章は日本語のテキスト読み上げをテストするためのものです。"  # Long
        ]
        
        for i, text in enumerate(test_texts):
            print(f"\nTest {i+1}: Converting '{text}' to speech")
            output_file = f"/app/data/debug_test_{i+1}.wav"
            tts.tts_to_file(text=text, file_path=output_file)
            
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"✓ Audio generated successfully: {size} bytes")
            else:
                print("✗ Failed to generate audio")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== TTS Debug/Test Utility ===")
    success = test_tts_functionality()
    sys.exit(0 if success else 1) 