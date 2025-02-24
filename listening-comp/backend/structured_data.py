from typing import List, Dict, Optional
from chat import LocalLLMChat

class TranscriptStructurer:
    def __init__(self):
        """Initialize the TranscriptStructurer with LocalLLMChat"""
        self.llm = LocalLLMChat()

    def read_transcript(self, filename: str) -> Optional[str]:
        """Read transcript from file"""
        try:
            with open(f"./transcripts/{filename}.txt", 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading transcript: {str(e)}")
            return None

    def extract_questions(self, transcript: str) -> List[Dict[str, str]]:
        """Extract questions from transcript using LLM"""
        prompt = """
        Extract the JLPT listening practice questions from this transcript. 
        For each question, format it as follows:

        Question #:
        Introduction:
        [The context or setup before the conversation]

        Conversation:
        [The dialogue between speakers]

        Question:
        [The actual question being asked]

        ---

        Transcript:
        {transcript}
        """

        try:
            response = self.llm.generate_response(prompt.format(transcript=transcript))
            return response if response else ""
        except Exception as e:
            print(f"Error extracting questions: {str(e)}")
            return ""

    def save_structured_data(self, questions: str, filename: str) -> bool:
        """Save structured questions to text file"""
        try:
            output_file = f"./structured/{filename}_structured.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(questions)
            return True
        except Exception as e:
            print(f"Error saving structured data: {str(e)}")
            return False

def main(video_id: str):
    """Main function to process transcript and extract structured data"""
    structurer = TranscriptStructurer()
    
    # Read transcript
    transcript = structurer.read_transcript(video_id)
    if not transcript:
        print("Failed to read transcript")
        return

    # Extract questions
    questions = structurer.extract_questions(transcript)
    print(questions)
    if not questions:
        print("Failed to extract questions")
        return
    
    # Save structured data
    if structurer.save_structured_data(questions, video_id):
        print(f"Structured data saved successfully to {video_id}_structured.txt")
    else:
        print("Failed to save structured data")


if __name__ == "__main__":
    video_id = "sY7L5cfCWno"  # Example video ID
    main(video_id)
