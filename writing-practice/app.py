import gradio as gr
import requests
import json
import random
from manga_ocr import MangaOcr
from localllm import LocalLLM  # Your LocalLLM wrapper

# Initialize components
llm = LocalLLM()  # Your local LLM setup
mocr = MangaOcr()  # Manga OCR for handwriting recognition

# Create a study session
def create_study_session(group_id, activity_id=2):  # activity_id 2 is "Writing Practice"
    try:
        api_url = "http://localhost:8080/api/study_activities/sessions"
        response = requests.post(api_url, json={
            "group_id": group_id,
            "study_activity_id": activity_id
        })
        response.raise_for_status()
        data = response.json()
        
        print(f"Study session response: {json.dumps(data, indent=2)}")
        
        # Extract the session ID from the correct location in the response
        if "data" in data and isinstance(data["data"], dict):
            # Use study_session_id from the data object (your API format)
            session_id = data["data"].get("study_session_id")
        else:
            # Fallback to try other common formats
            session_id = data.get("id") or data.get("session_id")
            
        print(f"Extracted session ID: {session_id}")
        return session_id
    except requests.RequestException as e:
        print(f"Failed to create study session: {str(e)}")
        return None

# Submit review result to backend
def submit_review_result(session_id, word_id, is_correct):
    if not session_id or not word_id:
        print("Cannot submit review - missing session_id or word_id")
        return False
        
    try:
        api_url = f"http://localhost:8080/api/study_sessions/{session_id}/words/{word_id}/review"
        response = requests.post(api_url, json={"correct": is_correct})
        response.raise_for_status()
        print(f"Submitted review result: session={session_id}, word={word_id}, correct={is_correct}")
        return True
    except requests.RequestException as e:
        print(f"Failed to submit review result: {str(e)}")
        return False

# Improved vocabulary fetching function that handles different response formats
def fetch_vocabulary(group_id=1):
    # Define the endpoint
    api_url = f"http://localhost:8080/api/groups/{group_id}/words/raw"
    
    try:
        print(f"Attempting to fetch vocabulary from: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status()
        
        # Get the raw data
        data = response.json()
        print(f"Successfully fetched vocabulary from API: {len(data)} items")
        
        # Extract the word list - handle different possible formats
        vocabulary = []
        
        # Determine the format and process accordingly
        if isinstance(data, dict):
            # Format: {"group_id": 1, "group_name": "name", "words": [...]}
            if "words" in data:
                word_list = data["words"]
            # Format: {"data": [...]}
            elif "data" in data:
                word_list = data["data"]
            else:
                word_list = []
        else:
            # Already an array
            word_list = data
        
        # Process each word based on its format
        for word in word_list:
            if isinstance(word, dict):
                # Format: {"japanese": "...", "english": "...", "romaji": "..."}
                vocabulary.append({
                    "id": word.get("id", 0),  # Add ID field for tracking
                    "japanese": word.get("japanese", word.get("kanji", "")),
                    "english": word.get("english", ""),
                    "romaji": word.get("romaji", "")
                })
            elif isinstance(word, str):
                # Format: Just a string of Japanese
                vocabulary.append({
                    "id": 0,  # No ID available
                    "japanese": word,
                    "english": "",  # No English translation available
                    "romaji": ""    # No romaji available
                })
                
        print(f"Processed {len(vocabulary)} vocabulary items")
        return vocabulary
        
    except requests.RequestException as e:
        print(f"Failed to fetch from {api_url}: {str(e)}")
        # Fall back to mock data
        print("Using mock vocabulary data.")
        return [
            {"id": 1, "japanese": "食べる", "english": "to eat"},
            {"id": 2, "japanese": "飲む", "english": "to drink"},
            # ... other mock words with IDs ...
        ]

# Parse grading result to extract correct/incorrect status
def parse_grading_result(grading_text):
    # Simple parsing - check if the text contains "CORRECT"
    return "CORRECT" in grading_text.upper()

# Application states
SETUP_STATE = "setup"
PRACTICE_STATE = "practice"
REVIEW_STATE = "review"

# Core functions
def generate_sentence(word):
    prompt = f"Generate a simple sentence using the following word: {word}\n"
    prompt += "The grammar should be scoped to JLPTN5 grammar.\n"
    prompt += "You can use the following vocabulary to construct a simple sentence:\n"
    prompt += "- simple objects eg. book, car, ramen, sushi\n"
    prompt += "- simple verbs, to drink, to eat, to meet\n"
    prompt += "- simple times eg. tomorrow, today, yesterday"
    
    return llm.generate(prompt)

def grade_submission(image, target_sentence):
    # Transcribe the image
    transcription = mocr(image)
    
    # Get translation
    translation_prompt = f"Provide a literal translation of this Japanese text: {transcription}"
    translation = llm.generate(translation_prompt)
    
    # Simplified binary grading
    grading_prompt = f"""Evaluate this Japanese writing attempt:
    - Target English sentence: {target_sentence}
    - Transcribed Japanese: {transcription}
    - Translated back to English: {translation}
    
    Is this correct? Respond with only one of these options:
    - "CORRECT" if the meaning is accurately conveyed
    - "INCORRECT" if there are significant errors
    
    Then provide one brief sentence of feedback.
    """
    
    grading = llm.generate(grading_prompt)
    
    return transcription, translation, grading

def app_interface():
    vocabulary = fetch_vocabulary()
    
    with gr.Blocks() as app:
        # State variables
        current_state = gr.State(SETUP_STATE)
        current_sentence = gr.State("")
        current_word_id = gr.State(0)  # Track the current word ID
        session_id = gr.State(None)    # Track the study session ID
        
        gr.Markdown("# Japanese Writing Practice")
        
        # Setup State UI
        with gr.Group() as setup_ui:
            setup_heading = gr.Markdown("## Start Practice")
            group_selector = gr.Dropdown(
                label="Select Vocabulary Group",
                choices=[
                    {"label": "Animals", "value": 1},
                    {"label": "Greetings", "value": 2},
                    {"label": "Verbs", "value": 3},
                    {"label": "Adjectives", "value": 4}
                ],
                value=1
            )
            generate_btn = gr.Button("Generate Sentence")
        
        # Practice State UI
        with gr.Group(visible=False) as practice_ui:
            practice_heading = gr.Markdown("## Practice Writing")
            sentence_display = gr.Textbox(label="Write this sentence in Japanese:")
            image_input = gr.Image(label="Upload your handwritten Japanese", type="pil")
            submit_btn = gr.Button("Submit for Review")
        
        # Review State UI
        with gr.Group(visible=False) as review_ui:
            review_heading = gr.Markdown("## Review")
            original_sentence = gr.Textbox(label="Original Sentence:")
            transcription_output = gr.Textbox(label="Transcribed Japanese:")
            translation_output = gr.Textbox(label="Translation:")
            grading_output = gr.Textbox(label="Result:")  # Changed from "Grading" to "Result"
            next_btn = gr.Button("Next Question")
        
        # Functions for state transitions
        def generate_and_transition(group_id):
            # Make sure group_id is an integer
            if not isinstance(group_id, int):
                try:
                    group_id = int(group_id)
                except (ValueError, TypeError):
                    group_id = 1  # Default to group 1 if there's an issue
            
            # Create a study session
            session = create_study_session(group_id)
            
            # Get vocabulary for the selected group
            vocabulary = fetch_vocabulary(group_id)
            
            # Choose a random word
            word = random.choice(vocabulary)
            word_id = word.get("id", 0)
            japanese = word["japanese"]
            
            # Generate a sentence
            sentence = generate_sentence(japanese)
            
            return (
                PRACTICE_STATE, sentence, word_id, session,
                gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), 
                sentence
            )
        
        def submit_for_review(image, sentence, word_id, session_id):
            transcription, translation, grading = grade_submission(image, sentence)
            
            # Parse the grading result to get boolean
            is_correct = parse_grading_result(grading)
            
            # Submit the result to the backend
            submission_status = ""
            if session_id and word_id:
                success = submit_review_result(session_id, word_id, is_correct)
                if success:
                    submission_status = "✅ Result recorded in backend (session ID: {}, word ID: {})".format(session_id, word_id)
                else:
                    submission_status = "❌ Failed to record result in backend"
            else:
                submission_status = "⚠️ No session or word ID available - result not recorded"
            
            # Add the submission status to the grading feedback
            full_feedback = grading + "\n\n" + submission_status
            
            return (
                REVIEW_STATE, sentence, word_id, session_id,
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=True),
                sentence, transcription, translation, full_feedback
            )
        
        def next_question(session_id):
            # Pick a random word
            word = random.choice(vocabulary)
            word_id = word.get("id", 0)
            japanese = word["japanese"]
            
            # Generate a sentence
            sentence = generate_sentence(japanese)
            
            return (
                PRACTICE_STATE, sentence, word_id, session_id,
                gr.update(visible=False), gr.update(visible=True), gr.update(visible=False),
                sentence
            )
        
        # Connect the buttons to the functions
        generate_btn.click(
            generate_and_transition,
            inputs=[group_selector],
            outputs=[
                current_state, current_sentence, current_word_id, session_id,
                setup_ui, practice_ui, review_ui,
                sentence_display
            ]
        )
        
        submit_btn.click(
            submit_for_review,
            inputs=[image_input, current_sentence, current_word_id, session_id],
            outputs=[
                current_state, current_sentence, current_word_id, session_id,
                setup_ui, practice_ui, review_ui,
                original_sentence, transcription_output, translation_output, grading_output
            ]
        )
        
        next_btn.click(
            next_question,
            inputs=[session_id],
            outputs=[
                current_state, current_sentence, current_word_id, session_id,
                setup_ui, practice_ui, review_ui,
                sentence_display
            ]
        )
        
    return app

demo = app_interface()
demo.launch() 