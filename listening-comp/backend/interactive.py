# Initialize PyTorch first to avoid Streamlit file watcher issues
import torch
# Force initialization 
_ = torch.zeros(1)

from typing import Dict, List, Optional
from backend.rag import JLPTQuestionStore
from backend.chat import LocalLLMChat
import re
import random
import os

class InteractivePracticeGenerator:
    def __init__(self):
        """Initialize the practice generator with RAG capabilities"""
        print("Initializing InteractivePracticeGenerator...")
        self.question_store = JLPTQuestionStore()
        
        # Check current collection state
        count = len(self.question_store.collection.get()["ids"])
        print(f"Initial collection size: {count} documents")
        
        # Force reset collection and add questions
        try:
            # Delete and recreate collection to ensure clean start
            self._reset_collection()
            
            # Add hardcoded questions
            success = self._add_hardcoded_questions()
            
            if not success:
                print("Failed to add hardcoded questions, trying fallbacks")
                self._add_fallback_questions()
        except Exception as e:
            print(f"Error during collection initialization: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Final verification
        count = len(self.question_store.collection.get()["ids"])
        print(f"Final collection size: {count} documents")
        
        self.llm = LocalLLMChat()
        
        # Map practice types to section types
        self.practice_to_section = {
            "Dialogue Practice": "問題1",  # Conversation questions
            "Vocabulary Quiz": "問題2",    # Situation questions
            "Listening Exercise": "問題3"  # Action response questions
        }
    
    def generate_question(self, practice_type: str) -> Dict:
        """Generate a practice question based on selected type using RAG"""
        section_type = self.practice_to_section[practice_type]
        
        # Create context-appropriate query
        query = self._create_query_for_practice_type(practice_type)
        
        # Retrieve similar questions
        similar_questions = self.question_store.query_questions(
            query_text=query,
            section_type=section_type,
            n_results=2
        )
        
        # Generate new question using retrieved examples
        new_question = self._generate_with_examples(practice_type, similar_questions)
        
        # Add metadata
        new_question["similar_questions"] = similar_questions
        new_question["correct_index"] = random.randint(0, 3)  # Randomly select a correct answer
        
        return new_question
    
    def _create_query_for_practice_type(self, practice_type: str) -> str:
        """Create appropriate query based on practice type"""
        if practice_type == "Dialogue Practice":
            return "男の人と女の人が話しています。レストランでの会話。"
        elif practice_type == "Vocabulary Quiz":
            return "レストランでの状況。食べ物を注文する。"
        else:  # Listening Exercise
            return "レストランで食事をします。店員に話します。"
    
    def _generate_with_examples(self, practice_type: str, examples: List[Dict]) -> Dict:
        """Generate a new question using examples"""
        # Create context from retrieved questions
        context = "\n\n".join([q["question"] for q in examples])
        
        # Debug output
        print(f"Retrieved {len(examples)} examples for context")
        for i, ex in enumerate(examples):
            print(f"Example {i+1}: {ex['question'][:100]}...")
        
        # Generate prompt based on practice type
        prompt = self._create_prompt_for_practice_type(practice_type, context)
        
        # Generate response
        response = self.llm.generate_response(prompt)
        
        # Debug output
        print(f"LLM Response: {response}")
        
        # Parse response into structured format
        return self._parse_question_response(response, practice_type)
    
    def _create_prompt_for_practice_type(self, practice_type: str, context: str) -> str:
        """Create an appropriate prompt for the given practice type"""
        base_prompt = f"""
        You are a Japanese language teacher creating practice questions.
        
        Here are some examples of Japanese practice questions:
        {context}
        
        Create a new, unique Japanese practice question similar to these examples.
        YOUR RESPONSE MUST BE WRAPPED IN <question> </question> TAGS.
        
        IMPORTANT: All Japanese text in dialogues must be in pure Japanese only - NO English words mixed in.
        Use only Japanese words, kanji, hiragana and katakana in the actual Japanese sentences.
        """
        
        if practice_type == "Dialogue Practice":
            return base_prompt + """
            The question should be about a dialogue scenario between two people.
            Include:
            - A 'Setup' describing who is talking
            - A dialogue in pure Japanese (no English words mixed in)
            - A clear question about the dialogue in Japanese
            - 4 multiple-choice options labeled 1-4 in Japanese
            
            Follow the EXACT same format as the examples.
            
            IMPORTANT: Wrap your entire response in <question> </question> tags.
            """
        elif practice_type == "Vocabulary Quiz":
            return base_prompt + """
            The question should be about a specific situation.
            Include:
            - A 'Situation' description
            - A clear question about the situation in Japanese
            - 4 multiple-choice options labeled 1-4 in Japanese
            
            Follow the EXACT same format as the examples.
            
            IMPORTANT: Both the question and answers must be in pure Japanese.
            """
        else:  # Listening Exercise
            return base_prompt + """
            The question should be about how to respond in a specific situation.
            Include:
            - An 'Action' description
            - A 'Question' asking what to say in Japanese
            - 4 multiple-choice options labeled 1-4 with different Japanese phrases
            
            Follow the EXACT same format as the examples.
            """
    
    def _parse_question_response(self, response: str, practice_type: str) -> Dict:
        """Parse LLM output into structured question format"""
        try:
            # Add closing tag if missing but opening tag exists
            if '<question>' in response and '</question>' not in response:
                response += '</question>'
            
            # Extract question from response
            question_pattern = r'<question>(.*?)</question>'
            question_match = re.search(question_pattern, response, re.DOTALL)
            
            if not question_match:
                # Try without tags if can't find them
                print(f"WARNING: Could not find <question> tags in response, trying to parse directly")
                return self._parse_direct(response, practice_type)
                
            question_text = question_match.group(1).strip()
            print(f"Extracted question text: {question_text[:100]}...")
            
            # Different parsing based on practice type
            if practice_type == "Dialogue Practice":
                return self._parse_dialogue_question(question_text)
            elif practice_type == "Vocabulary Quiz":
                return self._parse_vocabulary_question(question_text)
            else:  # Listening Exercise
                return self._parse_listening_question(question_text)
                
        except Exception as e:
            print(f"ERROR parsing question response: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_question(practice_type)
    
    def _parse_direct(self, response: str, practice_type: str) -> Dict:
        """Parse response directly without relying on question tags"""
        try:
            if practice_type == "Dialogue Practice":
                # Look for Setup: and Options:
                setup_match = re.search(r'Setup:(.*?)(?:Question:|Dialogue:)', response, re.DOTALL)
                setup = setup_match.group(1).strip() if setup_match else "会話の場面です。"
                
                # Find the question
                question_match = re.search(r'(?:What|Which|Where|When|How|Why).*?\?', response, re.DOTALL)
                question = question_match.group(0).strip() if question_match else "質問に答えてください。"
                
                # Extract options - look for numbered options
                options = []
                option_matches = re.findall(r'(\d+)[\.|\)]?\s+(.*?)(?=\n\d+[\.|\)]|\Z)', response, re.DOTALL)
                for _, option in option_matches:
                    options.append(option.strip())
                
                # Ensure we have 4 options
                while len(options) < 4:
                    options.append(f"Option {len(options)+1}")
                
                return {
                    "setup": setup,
                    "question": question,
                    "options": options
                }
            
            # Similar approaches for other question types...
            else:
                return self._create_fallback_question(practice_type)
            
        except Exception as e:
            print(f"Error in direct parsing: {str(e)}")
            return self._create_fallback_question(practice_type)
    
    def _parse_dialogue_question(self, question_text: str) -> Dict:
        """Parse a dialogue practice question"""
        # Extract setup
        setup_match = re.search(r'Setup:(.*?)(?:Question:|Dialogue:)', question_text, re.DOTALL)
        setup = setup_match.group(1).strip() if setup_match else "会話の場面です。"
        
        # Extract question - more flexible pattern to catch Japanese questions
        question_match = re.search(r'Question:(.*?)(?:Options:|$)', question_text, re.DOTALL)
        question = question_match.group(1).strip() if question_match else "質問に答えてください。"
        
        # Extract options with more flexible pattern for Japanese
        options = []
        # Try to find numbered options in various formats
        option_matches = re.findall(r'(\d+)[\.。．：:\)）]?\s*(.*?)(?=\n\d+[\.。．：:\)）]?|$)', question_text, re.DOTALL)
        
        for _, option in option_matches:
            options.append(option.strip())
        
        # Debug the options extraction
        print(f"Found {len(options)} options: {options}")
        
        # Ensure we have 4 options
        while len(options) < 4:
            options.append(f"Option {len(options)+1}")
            
        return {
            "setup": setup,
            "question": question,
            "options": options
        }
    
    def _parse_vocabulary_question(self, question_text: str) -> Dict:
        """Parse a vocabulary quiz question"""
        # Extract situation
        situation_match = re.search(r'Situation:(.*?)Question:', question_text, re.DOTALL)
        situation = situation_match.group(1).strip() if situation_match else "状況の説明です。"
        
        # Extract question
        question_match = re.search(r'Question:(.*?)Options:', question_text, re.DOTALL)
        question = question_match.group(1).strip() if question_match else "質問に答えてください。"
        
        # Extract options (same as dialogue)
        options_text = re.search(r'Options:(.*)', question_text, re.DOTALL)
        options = []
        
        if options_text:
            options_lines = options_text.group(1).strip().split('\n')
            for line in options_lines:
                option_match = re.match(r'(\d+)\.\s+(.*)', line)
                if option_match:
                    options.append(option_match.group(2).strip())
        
        # Ensure we have 4 options
        while len(options) < 4:
            options.append(f"Option {len(options)+1}")
            
        return {
            "setup": situation,
            "question": question,
            "options": options
        }
    
    def _parse_listening_question(self, question_text: str) -> Dict:
        """Parse a listening exercise question"""
        # Extract action
        action_match = re.search(r'Action:(.*?)Question:', question_text, re.DOTALL)
        action = action_match.group(1).strip() if action_match else "行動の説明です。"
        
        # Extract question
        question_match = re.search(r'Question:(.*?)Options:', question_text, re.DOTALL)
        question = question_match.group(1).strip() if question_match else "何と言いますか。"
        
        # Extract options (same as others)
        options_text = re.search(r'Options:(.*)', question_text, re.DOTALL)
        options = []
        
        if options_text:
            options_lines = options_text.group(1).strip().split('\n')
            for line in options_lines:
                option_match = re.match(r'(\d+)\.\s+(.*)', line)
                if option_match:
                    options.append(option_match.group(2).strip())
        
        # Ensure we have 4 options
        while len(options) < 4:
            options.append(f"Option {len(options)+1}")
            
        return {
            "setup": action,
            "question": question,
            "options": options
        }
    
    def _create_fallback_question(self, practice_type: str) -> Dict:
        """Create a fallback question if parsing fails"""
        if practice_type == "Dialogue Practice":
            return {
                "setup": "男の人と女の人がレストランで話しています。",
                "question": "男の人は何を注文しますか。",
                "options": ["コーヒー", "紅茶", "ラーメン", "カレー"]
            }
        elif practice_type == "Vocabulary Quiz":
            return {
                "setup": "レストランで食事をしています。",
                "question": "「お会計お願いします」は英語で何ですか。",
                "options": ["Check, please", "Menu, please", "Water, please", "Thank you"]
            }
        else:  # Listening Exercise
            return {
                "setup": "レストランで注文します。",
                "question": "何と言いますか。",
                "options": ["メニューをください", "お勘定をお願いします", "水をください", "ありがとうございます"]
            }

    def _add_fallback_questions(self):
        """Add some minimal fallback questions directly to ChromaDB"""
        print("Adding fallback questions...")
        
        # Create a set of minimal example questions
        questions = [
            {
                'content': '<question>Setup: A man and woman are at a restaurant.\nQuestion: What would the man like to order?\nOptions:\n1. Coffee\n2. Tea\n3. Ramen\n4. Rice</question>',
                'metadata': {'video_id': 'fallback', 'section': '問題1', 'type': 'conversation'}
            },
            {
                'content': '<question>Situation: At a train station.\nQuestion: How do you ask for a ticket?\nOptions:\n1. Kippu o kudasai\n2. Densha wa doko desu ka\n3. Sumimasen\n4. Arigatou gozaimasu</question>',
                'metadata': {'video_id': 'fallback', 'section': '問題2', 'type': 'situation'}
            },
            {
                'content': '<question>Action: Apologizing for being late.\nQuestion: What would you say?\nOptions:\n1. Osoku natte sumimasen\n2. Ohayou gozaimasu\n3. Arigatou gozaimasu\n4. Sayounara</question>',
                'metadata': {'video_id': 'fallback', 'section': '問題3', 'type': 'action'}
            }
        ]
        
        try:
            # Add directly to ChromaDB
            self.question_store.collection.add(
                documents=[q['content'] for q in questions],
                metadatas=[q['metadata'] for q in questions],
                ids=[f"fallback_{i}" for i in range(len(questions))]
            )
            print(f"Added {len(questions)} fallback questions")
            return True
        except Exception as e:
            print(f"Error adding fallback questions: {str(e)}")
            return False

    def _add_hardcoded_questions(self):
        """Add hardcoded questions directly to bypass file system issues"""
        print("Adding hardcoded questions...")
        
        # Hardcoded questions for each type
        hardcoded = [
            {
                'content': '<question>Setup: A man and woman are at a restaurant.\nThe man is looking at the menu.\nWoman: "何を注文しますか？"\nMan: "ラーメンを食べたいです。"\nQuestion: What does the man want to eat?\nOptions:\n1. Rice\n2. Ramen\n3. Sushi\n4. Tempura</question>',
                'metadata': {'video_id': 'hardcoded', 'section': '問題1', 'type': 'conversation'}
            },
            {
                'content': '<question>Situation: You are at the train station and need to buy a ticket.\nQuestion: How do you ask for a ticket in Japanese?\nOptions:\n1. チケットをください\n2. 切符をください\n3. 電車はどこですか\n4. いくらですか</question>',
                'metadata': {'video_id': 'hardcoded', 'section': '問題2', 'type': 'situation'}
            },
            {
                'content': '<question>Action: You want to order food at a restaurant.\nQuestion: What would you say to call the waiter?\nOptions:\n1. すみません\n2. ありがとう\n3. おはようございます\n4. さようなら</question>',
                'metadata': {'video_id': 'hardcoded', 'section': '問題3', 'type': 'action'}
            }
        ]
        
        try:
            # Add directly to ChromaDB
            self.question_store.collection.add(
                documents=[q['content'] for q in hardcoded],
                metadatas=[q['metadata'] for q in hardcoded],
                ids=[f"hardcoded_{i}" for i in range(len(hardcoded))]
            )
            print(f"Added {len(hardcoded)} hardcoded questions")
            print(f"Collection now has {len(self.question_store.collection.get()['ids'])} documents")
            return True
        except Exception as e:
            print(f"Error adding hardcoded questions: {str(e)}")
            return False

    def _reset_collection(self):
        """Reset the collection to ensure clean state"""
        print("Resetting collection...")
        collection_name = self.question_store.collection.name
        
        # Try to delete the collection
        try:
            self.question_store.client.delete_collection(collection_name)
            print(f"Deleted collection: {collection_name}")
        except Exception as e:
            print(f"Error deleting collection (may not exist yet): {str(e)}")
        
        # Recreate the collection with the same embedding function
        embedding_func = self.question_store.collection._embedding_function
        self.question_store.collection = self.question_store.client.create_collection(
            name=collection_name,
            embedding_function=embedding_func
        )
        print(f"Recreated collection: {collection_name}")
