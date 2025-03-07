# Monkey patch PyTorch's load function to make it work with TTS
import torch
from functools import wraps

# Store the original load function
original_load = torch.load

# Create a patched version that sets weights_only=False
@wraps(original_load)
def patched_load(*args, **kwargs):
    # Force weights_only to False for TTS models
    kwargs['weights_only'] = False
    return original_load(*args, **kwargs)

# Replace the function
torch.load = patched_load
print("PyTorch load function patched")

# Add RAdam to safe globals if available
try:
    import torch.serialization
    from importlib import import_module
    
    # Try to dynamically import RAdam class
    try:
        radam_module = import_module('TTS.utils.radam')
        if hasattr(radam_module, 'RAdam'):
            if hasattr(torch.serialization, 'add_safe_globals'):
                torch.serialization.add_safe_globals([radam_module.RAdam])
                print("Added RAdam to PyTorch safe globals")
    except (ImportError, AttributeError) as e:
        print(f"Note: RAdam import not available yet: {e}")
        
except Exception as e:
    print(f"Note: Could not patch safe globals: {e}") 