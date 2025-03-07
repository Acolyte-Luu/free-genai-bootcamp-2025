import os
import json
import re
import subprocess
import tempfile
from typing import Dict, List, Tuple

# Import LLM for conversation formatting
from backend.chat import LocalLLMChat

class JapaneseAudioGenerator:
    def __init__(self):
        """Initialize the audio generator with Docker TTS capabilities"""
        self.llm = LocalLLMChat()
        self.temp_dir = tempfile.mkdtemp()
        
        # We'll use a Docker container for TTS
        self.docker_container = "tts-service"
        self.shared_volume = "/app/data"
        
        # Check if Docker and the TTS container are available
        self.tts_available = self._check_tts_available()
        
        print(f"TTS {'available' if self.tts_available else 'not available - run the TTS Docker container first'}")
    
    def _check_tts_available(self) -> bool:
        """Check if Docker TTS is available"""
        try:
            # Check if Docker is running and our container exists
            result = subprocess.run(
                ["docker", "ps", "-q", "-f", f"name={self.docker_container}"], 
                capture_output=True, text=True
            )
            return bool(result.stdout.strip())
        except Exception:
            return False
    
    def generate_audio_for_question(self, question: Dict) -> str:
        """Generate audio file for a question and return the path"""
        # Extract content based on question type
        practice_type = question.get("practice_type", "Dialogue Practice")
        
        # Parse into speakers and text
        audio_parts = self._parse_question_to_audio_parts(question, practice_type)
        
        if not self.tts_available:
            print("TTS Docker container not available - falling back to text script")
            return self._generate_text_script(audio_parts)
            
        # Generate audio files for each part
        audio_files = []
        for speaker, text, gender in audio_parts:
            # Generate audio file for this part
            audio_path = self._generate_audio_segment(text, gender, speaker)
            if audio_path:
                audio_files.append(audio_path)
        
        if not audio_files:
            return self._generate_text_script(audio_parts)
            
        # Combine audio files with ffmpeg if available
        try:
            output_path = os.path.join(self.temp_dir, "combined_audio.mp3")
            self._combine_audio_files(audio_files, output_path)
            return output_path
        except Exception as e:
            print(f"Error combining audio: {e}")
            # Return the first audio file if combination fails
            return audio_files[0] if audio_files else self._generate_text_script(audio_parts)
    
    def _generate_text_script(self, audio_parts):
        """Generate a text script as fallback when TTS is unavailable"""
        output_path = os.path.join(self.temp_dir, "audio_script.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Japanese Audio Script\n\n")
            for speaker, text, gender in audio_parts:
                f.write(f"**{speaker}**: {text}\n\n")
            f.write("\n(Text-based fallback because TTS Docker container is not available)")
        
        return output_path
    
    def _parse_question_to_audio_parts(self, question: Dict, practice_type: str) -> List[Tuple[str, str, str]]:
        """Parse a question into audio parts with speakers, text, and gender"""
        setup = question.get("setup", "")
        question_text = question.get("question", "")
        
        # Use the LLM to format as a multi-speaker dialogue
        prompt = f"""
        Convert this Japanese language practice question into a dialogue script for audio recording.
        Format the output as JSON with speakers, their lines, and gender (male/female).
        
        Practice Type: {practice_type}
        Setup: {setup}
        
        For dialogue practice, extract the conversation and make it natural.
        Include an announcer who introduces the scenario and asks the question at the end.
        
        Question: {question_text}
        
        Format the output EXACTLY like this example:
        {{
            "parts": [
                {{"speaker": "Announcer", "text": "これから会話を聞いてください。レストランでの会話です。", "gender": "announcer"}},
                {{"speaker": "Woman", "text": "何を注文しますか？", "gender": "female"}},
                {{"speaker": "Man", "text": "ラーメンを食べたいです。", "gender": "male"}},
                {{"speaker": "Announcer", "text": "質問です。男の人は何を注文しましたか？", "gender": "announcer"}}
            ]
        }}
        
        IMPORTANT: Ensure all Japanese text is grammatically correct and natural.
        """
        
        # Generate the formatted dialogue
        dialogue_json = self.llm.generate_response(prompt)
        
        # Extract JSON from the response
        try:
            # Find the JSON part in the response
            json_match = re.search(r'\{.*\}', dialogue_json, re.DOTALL)
            if json_match:
                dialogue_json = json_match.group(0)
            
            # Clean up the JSON to fix common formatting errors
            dialogue_json = dialogue_json.replace("'", "\"")  # Replace single quotes with double quotes
            dialogue_json = re.sub(r',\s*}', '}', dialogue_json)  # Remove trailing commas
            
            dialogue_data = json.loads(dialogue_json)
            return [(part["speaker"], part["text"], part["gender"]) for part in dialogue_data["parts"]]
        except Exception as e:
            print(f"Error parsing dialogue JSON: {e}")
            print(f"Raw JSON: {dialogue_json}")
            # Fallback to a simple format
            return [
                ("Announcer", f"これから{practice_type}の問題です。", "announcer"),
                ("Announcer", setup, "announcer"),
                ("Announcer", question_text, "announcer")
            ]
    
    def _generate_audio_segment(self, text: str, gender: str, speaker: str) -> str:
        """Generate audio for a text segment using Docker TTS"""
        # Add natural context to short text
        original_text = text
        if len(text) < 10:  # Conservative minimum threshold
            # Choose appropriate natural context based on text type
            if any(char in text for char in "?？"):
                text = f"質問です。{text}"  # "Here's a question: {text}"
            elif speaker == "Announcer":
                text = f"アナウンサー：{text}"  # "Announcer: {text}"
            elif "：" in text or ":" in text:
                text = f"会話です。{text}"  # "Here's a conversation: {text}"
            else:
                text = f"次の言葉：{text}"  # "The following phrase: {text}"
            
            print(f"Text was too short, extended from '{original_text}' to '{text}'")
        
        # Generate a unique filename
        safe_filename = re.sub(r'[^\w\-_]', '_', speaker) + "_" + str(abs(hash(text)))
        output_file = os.path.join(self.temp_dir, f"{safe_filename}.wav")
        
        try:
            # Prepare a text file with the content (to handle quotes, special chars)
            escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$')
            text_file = f"/app/temp_{safe_filename}.txt"
            
            cmd_create_text = [
                "docker", "exec", self.docker_container,
                "bash", "-c", f"cat > {text_file} << 'EOTTEXT'\n{escaped_text}\nEOTTEXT"
            ]
            print(f"Creating text file with command: {' '.join(cmd_create_text)}")
            
            # Create text file in container
            subprocess.run(cmd_create_text, check=True)
            
            # Select model based on speaker and gender - using only kokoro model with different parameters
            if speaker.lower() == "announcer":
                # Distinct announcer voice - slower, more formal
                model = "tts_models/ja/kokoro/tacotron2-DDC"
                params = ["--speed", "0.85"]  # Slightly slower
            elif gender.lower() == "female":
                # Female voice - slightly higher speed for female voice effect
                model = "tts_models/ja/kokoro/tacotron2-DDC" 
                params = ["--speed", "1.1"]  # Slightly faster for female effect
            elif gender.lower() == "male":
                # Male voice - slightly lower speed for male voice effect
                model = "tts_models/ja/kokoro/tacotron2-DDC"
                params = ["--speed", "0.95"]  # Slightly slower
            else:
                # Default voice
                model = "tts_models/ja/kokoro/tacotron2-DDC"
                params = []
            
            # Setup shared directory paths
            shared_dir = os.path.join(os.getcwd(), "../audio_data")
            os.makedirs(shared_dir, exist_ok=True)
            out_filename = f"{safe_filename}.wav"
            
            # Execute TTS in Docker
            cmd = [
                "docker", "exec", self.docker_container,
                "python", "/app/patched_tts.py",
                f"--text-file={text_file}",
                f"/app/data/{out_filename}",
                model,
            ]
            
            # Add each parameter separately to the command
            if params:
                cmd.extend(params)
            
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"Docker TTS error: {result.stderr}")
                # Run the debug command directly to get more info
                debug_cmd = [
                    "docker", "exec", self.docker_container,
                    "python", "-c", 
                    "exec(open('/app/pytorch_patch.py').read()); "  # Apply the patch first
                    f"from TTS.api import TTS; print('Available models:'); "
                    f"print(TTS().list_models()); "
                    f"print('Loading model {model}...'); tts=TTS(model_name='{model}'); "
                    f"print('Model loaded successfully')"
                ]
                print("Running debug command to check TTS models...")
                debug_result = subprocess.run(debug_cmd, capture_output=True, text=True)
                print(f"Debug output: {debug_result.stdout}")
                if debug_result.stderr:
                    print(f"Debug errors: {debug_result.stderr}")
                
                # Check if temp file exists
                check_cmd = ["docker", "exec", self.docker_container, "cat", text_file]
                check_result = subprocess.run(check_cmd, capture_output=True, text=True)
                print(f"Text file contents: {check_result.stdout}")
                
                # Check directory permissions
                dir_cmd = ["docker", "exec", self.docker_container, "ls", "-la", "/app/data"]
                dir_result = subprocess.run(dir_cmd, capture_output=True, text=True)
                print(f"Output directory contents: {dir_result.stdout}")
                return None
            
            # Copy the generated audio from shared directory to our temp dir
            shared_output_file = os.path.join(shared_dir, out_filename)
            if os.path.exists(shared_output_file):
                subprocess.run(["cp", shared_output_file, output_file])
                return output_file
            else:
                print(f"Output file not found: {shared_output_file}")
                return None
        except Exception as e:
            print(f"Error generating audio segment: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _combine_audio_files(self, audio_files: List[str], output_path: str) -> None:
        """Combine multiple audio files into one using ffmpeg"""
        # Create a file list for ffmpeg
        list_file = os.path.join(self.temp_dir, "files.txt")
        with open(list_file, "w") as f:
            for audio_file in audio_files:
                f.write(f"file '{audio_file}'\n")
        
        # Combine using ffmpeg
        result = subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
            "-i", list_file, "-c:a", "libmp3lame", "-q:a", "2", output_path
        ], capture_output=True)
        
        if result.returncode != 0:
            print(f"ffmpeg error: {result.stderr.decode()}")
            raise Exception("Failed to combine audio files") 