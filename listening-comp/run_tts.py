#!/usr/bin/env python3

# Apply the patch first
with open("/app/pytorch_patch.py") as f:
    exec(f.read())

# Then import and use the TTS functions
import sys
from patched_tts import synthesize_speech

# Just pass all arguments through
if __name__ == "__main__":
    # Get the input file, output file, and model
    args = sys.argv[1:]
    
    # Run the patched TTS script with all arguments
    import subprocess
    result = subprocess.run([sys.executable, "/app/patched_tts.py"] + args)
    sys.exit(result.returncode) 