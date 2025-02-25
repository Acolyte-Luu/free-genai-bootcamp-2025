from typing import List, Dict, Optional
from chat import LocalLLMChat

class TranscriptStructurer:
    def __init__(self):
        self.llm = LocalLLMChat()
        self.prompts = {
            1: """SYSTEM: You are a SILENT text extractor for dialogue-based questions. Output ONLY the extracted content.

                PATTERN TO MATCH:
                [A]が[B]と話しています。
                [Question ending in か。]
                [Numbered options]

                EXAMPLE 1:
                男の人と店の人が話しています。
                お手洗いはどこですか。
                1. エレベーター
                2. 階段の横
                3. 窓際
                4. 出口

                EXAMPLE 2:
                学生と先生が話しています。
                何時から始まりますか。
                1. 9時
                2. 10時
                3. 11時
                4. 12時

                RULES FOR 問題1:
                1. Setup MUST:
                   - End with 話しています。
                   - Include who is talking
                   - Be a single sentence

                2. Question MUST:
                   - Be a single question
                   - End with か。
                   - Not include dialogue

                3. Options MUST:
                   - Start with 1. 2. 3. 4.
                   - Be single answers
                   - Not include dialogue
                   - Not include explanations

                OUTPUT FORMAT:
                <question>
                Setup: [EXACT setup text]
                Question: [EXACT question text]
                Options:
                1. [single answer]
                2. [single answer]
                3. [single answer]
                4. [single answer]
                </question>

                CRITICAL RULES:
                × NO dialogue in options
                × NO long explanations
                × ONE answer per option
                × EXACT number format
                × MUST use <question> tags
                × MUST follow output format exactly

                START EXTRACTION:
                {transcript}
                """,

            2: """SYSTEM: You are a SILENT text extractor for situation-based questions. Output ONLY the extracted content.

                PATTERN TO MATCH:
                [Situation description]
                [Question ending in か。]
                [Numbered options]

                EXAMPLE - CORRECT EXTRACTION:
                Input:
                女の人と男の人が話しています。
                2人はいつ行きますか。
                女の人：来週の日曜日は暇ですか。
                男の人：はい、大丈夫ですよ。
                女の人：では日曜日に行きましょう。
                男の人：そうですね。

                Output:
                <question>
                Situation: 女の人と男の人が話しています。
                Question: 2人はいつ行きますか。
                Options:
                1. 来週の日曜日
                2. 今日
                3. 明日
                4. 来月
                </question>

                EXAMPLE - INCORRECT OPTIONS:
                ❌ BAD OPTIONS (contain dialogue):
                1. 来週の日曜日は暇ですか
                2. はい、大丈夫ですよ
                3. では日曜日に行きましょう
                4. そうですね

                ✓ GOOD OPTIONS (simple answers):
                1. 来週の日曜日
                2. 今日
                3. 明日
                4. 来月

                RULES FOR OPTIONS:
                1. Options MUST be:
                   - Single phrases or words
                   - Direct answers to the question
                   - NOT dialogue fragments
                   - NOT questions
                   - NOT explanations

                2. Extract ONLY the core answer:
                   "山田さんお昼一緒に食べませんか" → "学生食堂"
                   "学生食堂が新しくなったから行きませんか" → "学生食堂"
                   "今日は天気がいいから外で食べたいです" → "外"
                   "桜公園まで行きましょう" → "桜公園"

                OUTPUT FORMAT:
                <question>
                Situation: [EXACT situation text]
                Question: [EXACT question text]
                Options:
                1. [simple answer - NOT dialogue]
                2. [simple answer - NOT dialogue]
                3. [simple answer - NOT dialogue]
                4. [simple answer - NOT dialogue]
                </question>

                CRITICAL RULES:
                × NO dialogue in options
                × NO questions in options
                × NO long explanations
                × ONE answer per option
                × EXACT number format
                × MUST use <question> tags
                × MUST follow output format exactly

                START EXTRACTION:
                {transcript}
                """,

            3: """SYSTEM: You are a SILENT text extractor with focus on Options. Output ONLY the extracted content.

                PATTERN EXAMPLES:

                問題3:
                Input:
                電車に乗ります。
                何と言いますか。
                1. すみません
                2. ありがとう
                3. おはよう

                Output:
                <question>
                Action: 電車に乗ります。
                Question: 何と言いますか。
                Options:
                1. すみません
                2. ありがとう
                3. おはよう
                </question>

                RULES FOR OPTIONS:
                1. Look for these EXACT patterns:
                   1. [text]
                   2. [text]
                   3. [text]

                2. Options MUST:
                   - Start with number + period (1. 2. 3.)
                   - Be complete phrases
                   - Not include dialogue
                   - Not include explanations

                CRITICAL RULES:
                1. Output ONLY <question> blocks
                2. NO explanations
                3. NO processing steps
                4. NO markers or tags
                5. EXACT text copy only
                6. Keep original numbering
                7. Keep original punctuation
                8. ONE option per number
                9. NO dialogue in options
                10. NO partial phrases

                START EXTRACTION:
                {transcript}
                """
        }

    def extract_section(self, transcript: str, section: int) -> str:
        """Extract questions from a specific section with improved validation"""
        try:
            # Validate section exists
            section_marker = f"問題{section}"
            if section_marker not in transcript:
                print(f"Error: Section {section_marker} not found")
                return ""

            # Extract section boundaries
            section_start = transcript.find(section_marker)
            next_section = transcript.find(f"問題{section+1}")
            if next_section == -1:  # If it's the last section
                section_text = transcript[section_start:]
            else:
                section_text = transcript[section_start:next_section]

            # Process with LLM using stricter parameters
            prompt = self.prompts[section].format(transcript=section_text)
            response = self.llm.generate_response(
                prompt,
                {
                    "temperature": 0.01,  # Very strict
                    "top_p": 0.1,        # Very focused
                    "frequency_penalty": 0.0,  # Allow repeating exact text
                    "presence_penalty": 0.0    # Allow repeating exact text
                }
            )

            # Validate response format
            if "<question>" not in response:
                print(f"Error: Invalid response format for section {section}")
                return ""

            return response

        except Exception as e:
            print(f"Error processing section {section}: {str(e)}")
            return ""

    def read_transcript(self, filename: str) -> Optional[str]:
        """Read transcript from file"""
        try:
            with open(f"./transcripts/{filename}.txt", 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading transcript: {str(e)}")
            return None

    def save_section(self, content: str, filename: str, section: int) -> bool:
        """Save a single section to a file"""
        try:
            section_file = f"./structured/{filename}_問題{section}.txt"
            with open(section_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved 問題{section} to {section_file}")
            return True
        except Exception as e:
            print(f"Error saving section {section}: {str(e)}")
            return False

def main(video_id: str):
    """Process transcript and extract structured data by section"""
    structurer = TranscriptStructurer()
    
    # Read transcript
    transcript = structurer.read_transcript(video_id)
    if not transcript:
        print("Failed to read transcript")
        return

    # Process each section
    for section in [1, 2, 3]:
        questions = structurer.extract_section(transcript, section)
        if questions:
            if structurer.save_section(questions, video_id, section):
                print(f"Section {section} processed successfully")
            else:
                print(f"Failed to save section {section}")
        else:
            print(f"Failed to extract section {section}")

if __name__ == "__main__":
    video_id = "sY7L5cfCWno"
    main(video_id)
