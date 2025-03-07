#!/usr/bin/env python3

import sys
import os
import argparse
from TTS.api import TTS
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("TTS operation timed out")

# Set timeout for TTS operations (30 seconds)
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)

def synthesize_speech(text, output_file, model_name):
    """
    Convert text to speech using the specified TTS model and save to output file.
    
    Args:
        text (str): The text to convert to speech
        output_file (str): Path to save the output WAV file
        model_name (str): Name of the TTS model to use
    """
    try:
        print(f"Initializing TTS with model: {model_name}")
        tts = TTS(model_name=model_name)
        
        print(f"Creating output directory: {os.path.dirname(output_file)}")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        print(f"Generating speech from text: {text[:50]}...")
        tts.tts_to_file(text=text, file_path=output_file)
        
        # Clear the alarm
        signal.alarm(0)
        
        print(f"Successfully generated speech to {output_file}")
        return True
    except TimeoutError as e:
        print(f"Timeout error: {str(e)}", file=sys.stderr)
        return False
    except Exception as e:
        import traceback
        print(f"Error generating speech: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate TTS audio from text")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("text", nargs="?", help="Text to synthesize")
    group.add_argument("--text-file", help="File containing text to synthesize")
    parser.add_argument("output", help="Output WAV file path")
    parser.add_argument("model", help="TTS model name")
    
    args = parser.parse_args()
    
    if args.text_file:
        with open(args.text_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    else:
        text = args.text
    
    success = synthesize_speech(text, args.output, args.model)
    sys.exit(0 if success else 1) 