# Initialize PyTorch first to avoid Streamlit file watcher issues
import torch
# Force initialization 
_ = torch.zeros(1)

import streamlit as st
from typing import Dict
import json
from collections import Counter
import re
from datetime import datetime

import sys
import os
# Add parent directory to path BEFORE importing backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import backend modules AFTER path setup
import backend.rag
import backend.interactive

from backend.chat import LocalLLMChat
from backend.get_transcript import YouTubeTranscriptDownloader
from backend.audio_generator import JapaneseAudioGenerator


# Page config
st.set_page_config(
    page_title="Japanese Learning Assistant",
    page_icon="🎌",
    layout="wide"
)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize audio generator in session state
if 'audio_generator' not in st.session_state:
    st.session_state.audio_generator = JapaneseAudioGenerator()

def render_header():
    """Render the header section"""
    st.title("🎌 Japanese Learning Assistant")
    st.markdown("""
    Transform YouTube transcripts into interactive Japanese learning experiences.
    
    This tool demonstrates:
    - Base LLM Capabilities
    - RAG (Retrieval Augmented Generation)
    - Amazon Bedrock Integration
    - Agent-based Learning Systems
    """)

def render_sidebar():
    """Render the sidebar with component selection"""
    with st.sidebar:
        st.header("Development Stages")
        
        # Main component selection
        selected_stage = st.radio(
            "Select Stage:",
            [
                "1. Chat with LocalLLM",
                "2. Raw Transcript",
                "3. Structured Data",
                "4. RAG Implementation",
                "5. Interactive Learning"
            ]
        )
        
        # Stage descriptions
        stage_info = {
            "1. Chat with LocalLLM": """
            **Current Focus:**
            - Basic Japanese learning
            - Understanding LLM capabilities
            - Identifying limitations
            """,
            
            "2. Raw Transcript": """
            **Current Focus:**
            - YouTube transcript download
            - Raw text visualization
            - Initial data examination
            """,
            
            "3. Structured Data": """
            **Current Focus:**
            - Text cleaning
            - Dialogue extraction
            - Data structuring
            """,
            
            "4. RAG Implementation": """
            **Current Focus:**
            - Bedrock embeddings
            - Vector storage
            - Context retrieval
            """,
            
            "5. Interactive Learning": """
            **Current Focus:**
            - Scenario generation
            - Audio synthesis
            - Interactive practice
            """
        }
        
        st.markdown("---")
        st.markdown(stage_info[selected_stage])
        
        return selected_stage

def render_chat_stage():
    """Render an improved chat interface"""
    st.header("Chat with LocalLLM")

    # Initialize BedrockChat instance if not in session state
    if 'local_llm_chat' not in st.session_state:
        st.session_state.local_llm_chat = LocalLLMChat()

    # Introduction text
    st.markdown("""
    Start by exploring Nova's base Japanese language capabilities. Try asking questions about Japanese grammar, 
    vocabulary, or cultural aspects.
    """)

    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Chat input area
    if prompt := st.chat_input("Ask about Japanese language..."):
        # Process the user input
        process_message(prompt)

    # Example questions in sidebar
    with st.sidebar:
        st.markdown("### Try These Examples")
        example_questions = [
            "How do I say 'Where is the train station?' in Japanese?",
            "Explain the difference between は and が",
            "What's the polite form of 食べる?",
            "How do I count objects in Japanese?",
            "What's the difference between こんにちは and こんばんは?",
            "How do I ask for directions politely?"
        ]
        
        for q in example_questions:
            if st.button(q, use_container_width=True, type="secondary"):
                # Process the example question
                process_message(q)
                st.rerun()

    # Add a clear chat button
    if st.session_state.messages:
        if st.button("Clear Chat", type="primary"):
            st.session_state.messages = []
            st.rerun()

def process_message(message: str):
    """Process a message and generate a response"""
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(message)

    # Generate and display assistant's response
    with st.chat_message("assistant", avatar="🤖"):
        response = st.session_state.local_llm_chat.generate_response(message)
        if response:
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})



def count_characters(text):
    """Count Japanese and total characters in text"""
    if not text:
        return 0, 0
        
    def is_japanese(char):
        return any([
            '\u4e00' <= char <= '\u9fff',  # Kanji
            '\u3040' <= char <= '\u309f',  # Hiragana
            '\u30a0' <= char <= '\u30ff',  # Katakana
        ])
    
    jp_chars = sum(1 for char in text if is_japanese(char))
    return jp_chars, len(text)

def render_transcript_stage():
    """Render the raw transcript stage"""
    st.header("Raw Transcript Processing")
    
    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="Enter a Japanese lesson YouTube URL"
    )
    
    # Download button and processing
    if url:
        if st.button("Download Transcript"):
            try:
                downloader = YouTubeTranscriptDownloader()
                transcript = downloader.get_transcript(url)
                if transcript:
                    # Store the raw transcript text in session state
                    transcript_text = "\n".join([entry['text'] for entry in transcript])
                    st.session_state.transcript = transcript_text
                    st.success("Transcript downloaded successfully!")
                else:
                    st.error("No transcript found for this video.")
            except Exception as e:
                st.error(f"Error downloading transcript: {str(e)}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Transcript")
        if st.session_state.transcript:
            st.text_area(
                label="Raw text",
                value=st.session_state.transcript,
                height=400,
                disabled=True
            )
    
        else:
            st.info("No transcript loaded yet")
    
    with col2:
        st.subheader("Transcript Stats")
        if st.session_state.transcript:
            # Calculate stats
            jp_chars, total_chars = count_characters(st.session_state.transcript)
            total_lines = len(st.session_state.transcript.split('\n'))
            
            # Display stats
            st.metric("Total Characters", total_chars)
            st.metric("Japanese Characters", jp_chars)
            st.metric("Total Lines", total_lines)
        else:
            st.info("Load a transcript to see statistics")

def render_structured_stage():
    """Render the structured data stage"""
    st.header("Structured Data Processing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dialogue Extraction")
        # Placeholder for dialogue processing
        st.info("Dialogue extraction will be implemented here")
        
    with col2:
        st.subheader("Data Structure")
        # Placeholder for structured data view
        st.info("Structured data view will be implemented here")

def render_rag_stage():
    """Render the RAG implementation stage"""
    st.header("RAG System")
    
    # Query input
    query = st.text_input(
        "Test Query",
        placeholder="Enter a question about Japanese..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retrieved Context")
        # Placeholder for retrieved contexts
        st.info("Retrieved contexts will appear here")
        
    with col2:
        st.subheader("Generated Response")
        # Placeholder for LLM response
        st.info("Generated response will appear here")

def load_question_history():
    """Load question history from a JSON file"""
    history_file = "question_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading history: {e}")
    return []

def save_question_history(history):
    """Save question history to a JSON file"""
    history_file = "question_history.json"
    try:
        with open(history_file, "w", encoding="utf-8") as file:
            json.dump(history, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

def render_interactive_stage():
    """Render the interactive learning stage with RAG"""
    st.header("Interactive Learning")
    
    # Initialize practice generator if not exists
    if 'practice_generator' not in st.session_state:
        from backend.interactive import InteractivePracticeGenerator
        st.session_state.practice_generator = InteractivePracticeGenerator()
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
        
    # Initialize question history from file if not exists
    if 'question_history' not in st.session_state:
        st.session_state.question_history = load_question_history()
    
    # Create a 2-column layout with sidebar for history
    col_main, col_history = st.columns([3, 1])
    
    with col_main:
        # Practice type selection
        practice_type = st.selectbox(
            "Select Practice Type",
            ["Dialogue Practice", "Vocabulary Quiz", "Listening Exercise"]
        )
        
        # Generate button
        if st.button("Generate New Practice Question"):
            with st.spinner("Generating question..."):
                try:
                    question_data = st.session_state.practice_generator.generate_question(practice_type)
                    
                    # Add timestamp and type to question data
                    question_data["timestamp"] = datetime.now().strftime("%H:%M:%S")
                    question_data["practice_type"] = practice_type
                    
                    st.session_state.current_question = question_data
                    
                    # Add to history (limited to last 10 questions)
                    st.session_state.question_history.append(question_data)
                    if len(st.session_state.question_history) > 10:
                        st.session_state.question_history.pop(0)  # Remove oldest
                    
                    # Save history to file
                    save_question_history(st.session_state.question_history)
                        
                except Exception as e:
                    st.error(f"Error generating question: {str(e)}")
        
        # Display current question
        if st.session_state.current_question:
            st.subheader("Practice Scenario")
            
            # Display setup/situation/action based on practice type
            current_type = st.session_state.current_question.get('practice_type', practice_type)
            if current_type == "Dialogue Practice":
                st.markdown(f"**Setup:** {st.session_state.current_question['setup']}")
            elif current_type == "Vocabulary Quiz":
                st.markdown(f"**Situation:** {st.session_state.current_question['setup']}")
            else:
                st.markdown(f"**Action:** {st.session_state.current_question['setup']}")
            
            st.markdown(f"**Question:** {st.session_state.current_question['question']}")
            
            # Display options
            options = st.session_state.current_question['options']
            selected = st.radio("Choose your answer:", 
                              [f"{i+1}. {option}" for i, option in enumerate(options)])
            
            # Get selected index (0-based)
            selected_index = int(selected.split('.')[0]) - 1
            
            # Check answer button
            if st.button("Check Answer"):
                correct_index = st.session_state.current_question["correct_index"]
                is_correct = selected_index == correct_index
                
                # Generate detailed feedback
                feedback = st.session_state.practice_generator.generate_answer_feedback(
                    st.session_state.current_question, 
                    selected_index
                )
                
                # Display result
                if is_correct:
                    st.success("✅ Correct! Great job!")
                else:
                    st.error(f"❌ Not quite. The correct answer is: {correct_index + 1}. {options[correct_index]}")
                
                # Display detailed feedback
                st.subheader("Explanation")
                st.markdown(feedback["feedback"])
                
                # Optionally add a "Learn More" section
                with st.expander("Learn More"):
                    st.info("Click to hear pronunciation (coming soon)")
            
            # Similar Questions section
            st.subheader("Similar Questions")
            
            # Show the retrieved similar questions
            if 'similar_questions' in st.session_state.current_question:
                for i, q in enumerate(st.session_state.current_question['similar_questions']):
                    with st.expander(f"Example {i+1}"):
                        st.markdown(q["question"])
            
            # Audio section
            st.subheader("Audio")
            if st.button("Generate Audio"):
                with st.spinner("Generating audio..."):
                    try:
                        # Generate audio for the current question
                        audio_path = st.session_state.audio_generator.generate_audio_for_question(
                            st.session_state.current_question
                        )
                        
                        # Store the path in session state
                        st.session_state.current_audio_path = audio_path
                        
                        # Show success message
                        st.success("Audio generated successfully!")
                    except Exception as e:
                        st.error(f"Error generating audio: {str(e)}")

            # Display audio player if we have a generated audio file
            if 'current_audio_path' in st.session_state and os.path.exists(st.session_state.current_audio_path):
                if st.session_state.current_audio_path.endswith('.mp3') or st.session_state.current_audio_path.endswith('.wav'):
                    # Display audio player for audio files
                    audio_file = open(st.session_state.current_audio_path, 'rb')
                    audio_bytes = audio_file.read()
                    audio_format = 'audio/mp3' if st.session_state.current_audio_path.endswith('.mp3') else 'audio/wav'
                    st.audio(audio_bytes, format=audio_format)
                elif st.session_state.current_audio_path.endswith('.txt'):
                    # Display text for TXT files (fallback)
                    with open(st.session_state.current_audio_path, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                    st.markdown(script_content)
                    st.warning("Audio generation requires additional dependencies. Install them with:")
                    st.code("pip install TTS\nsudo apt-get install ffmpeg  # or brew install ffmpeg for macOS")
            else:
                st.info("Click 'Generate Audio' to create spoken audio for this question")
        else:
            st.info("Click 'Generate New Practice Question' to start")
    
    # Question history sidebar
    with col_history:
        st.subheader("Question History")
        
        if not st.session_state.question_history:
            st.info("No questions in history yet")
        else:
            for i, past_q in enumerate(reversed(st.session_state.question_history)):
                # Create a unique key for each history item
                if st.button(f"{past_q['timestamp']} - {past_q['practice_type']}", key=f"history_{i}"):
                    st.session_state.current_question = past_q
                    st.rerun()

def main():
    render_header()
    selected_stage = render_sidebar()
    
    # Render appropriate stage
    if selected_stage == "1. Chat with LocalLLM":
        render_chat_stage()
    elif selected_stage == "2. Raw Transcript":
        render_transcript_stage()
    elif selected_stage == "3. Structured Data":
        render_structured_stage()
    elif selected_stage == "4. RAG Implementation":
        render_rag_stage()
    elif selected_stage == "5. Interactive Learning":
        render_interactive_stage()
    
    # Debug section at the bottom
    with st.expander("Debug Information"):
        st.json({
            "selected_stage": selected_stage,
            "transcript_loaded": st.session_state.transcript is not None,
            "chat_messages": len(st.session_state.messages)
        })

if __name__ == "__main__":
    main()