#!/usr/bin/env python3

# Import patch before anything else
exec(open("/app/pytorch_patch.py").read())

import sys
import os
import argparse
from TTS.api import TTS
import torch.serialization
import importlib

# Add the RAdam class to the safe globals list
try:
    # Import the RAdam class
    from TTS.utils.radam import RAdam
    # Add it to PyTorch's safe globals
    torch.serialization.add_safe_globals([RAdam])
    print("Successfully added RAdam to PyTorch safe globals")
except Exception as e:
    print(f"Warning: Failed to add RAdam to safe globals: {e}")
    # Try to find the module path
    try:
        tts_utils = importlib.import_module('TTS.utils')
        print(f"TTS.utils module path: {tts_utils.__file__}")
        print(f"Available in TTS.utils: {dir(tts_utils)}")
    except Exception as sub_e:
        print(f"Error inspecting TTS modules: {sub_e}")

def synthesize_speech(text, output_file, model_name, speaker_id=None, speed=1.0):
    """
    Convert text to speech using the specified TTS model and save to output file.
    
    Args:
        text (str): The text to convert to speech
        output_file (str): Path to save the output WAV file
        model_name (str): Name of the TTS model to use
        speaker_id (int): Speaker ID for multi-speaker models
        speed (float): Speaking speed (0.5-2.0)
    """
    try:
        print(f"Loading TTS model: {model_name}")
        tts = TTS(model_name=model_name)
        
        # Apply voice modification parameters if provided
        kwargs = {}
        if speaker_id is not None:
            kwargs["speaker_id"] = speaker_id
        
        print(f"Creating output directory: {os.path.dirname(output_file)}")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        print(f"Generating speech from {'text file' if text.startswith('/app/') else 'direct text'}")
        
        # If text is a file path, read from the file
        if text.startswith('/app/'):
            with open(text, 'r', encoding='utf-8') as f:
                text_content = f.read().strip()
        else:
            text_content = text
        
        # Generate speech with speed control
        tts.tts_to_file(text=text_content, file_path=output_file, **kwargs)
        
        # If speed is not 1.0, process with ffmpeg to adjust speed
        if speed != 1.0:
            import subprocess
            temp_file = output_file + ".temp.wav"
            subprocess.run(["mv", output_file, temp_file])
            
            # Use ffmpeg's atempo filter for speed adjustment
            # atempo valid range is 0.5 to 2.0, use multiple filters for more extreme values
            atempo_param = str(speed)
            if speed < 0.5:
                atempo_param = "0.5,0.5,0.5,0.5"  # Multiply effects for very slow
            elif speed > 2.0:
                atempo_param = "2.0,2.0,2.0,2.0"  # Multiply effects for very fast
                
            subprocess.run([
                "ffmpeg", "-i", temp_file, 
                "-filter:a", f"atempo={atempo_param}", 
                "-y", output_file
            ])
            
            # Clean up temp file
            subprocess.run(["rm", temp_file])
            
        print(f"Speech generated successfully. Output file: {output_file}")
        return True
    except Exception as e:
        import traceback
        print(f"Error generating speech: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate speech from text using TTS")
    parser.add_argument("--text", help="Text to synthesize")
    parser.add_argument("--text-file", help="File containing text to synthesize")
    parser.add_argument("output_file", help="Output audio file path")
    parser.add_argument("model", help="TTS model to use")
    parser.add_argument("--speaker_id", help="Speaker ID for multi-speaker models", type=int)
    parser.add_argument("--speed", help="Speaking speed (0.5-2.0)", type=float, default=1.0)
    
    args = parser.parse_args()
    
    # Get text from either --text or --text-file
    if args.text:
        text_input = args.text
    elif args.text_file:
        text_input = args.text_file
    else:
        print("Error: Either --text or --text-file must be provided")
        sys.exit(1)
    
    # Synthesize speech
    success = synthesize_speech(
        text_input, 
        args.output_file, 
        args.model,
        speaker_id=args.speaker_id, 
        speed=args.speed
    )
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1) 