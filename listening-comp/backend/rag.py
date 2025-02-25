from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions
import json
import os
from pathlib import Path

class JLPTQuestionStore:
    def __init__(self, persist_dir: str = "./chroma_db"):
        """Initialize ChromaDB with persistence and Japanese embeddings"""
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Delete existing collection if it exists
        try:
            self.client.delete_collection("jlpt-n5-listening")
        except:
            pass  # Collection might not exist yet
        
        # Use Japanese-optimized embedding function
        japanese_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="intfloat/multilingual-e5-large"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="jlpt-n5-listening",
            metadata={"description": "JLPT N5 Listening Questions"},
            embedding_function=japanese_embeddings
        )

    def process_question_file(self, file_path: str) -> List[Dict]:
        """Process a structured question file into individual questions with metadata"""
        try:
            # Extract metadata from filename (e.g., sY7L5cfCWno_問題1.txt)
            file_name = Path(file_path).stem
            video_id, section = file_name.split('_')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split content into individual questions
            questions = []
            for question in content.split('<question>'):
                if not question.strip():
                    continue
                    
                question = '<question>' + question.split('</question>')[0] + '</question>'
                
                # Extract components based on section type
                if section == '問題1':
                    metadata = {
                        'video_id': video_id,
                        'section': section,
                        'type': 'conversation',
                        'components': 'setup,dialogue,question,options'
                    }
                elif section == '問題2':
                    metadata = {
                        'video_id': video_id,
                        'section': section,
                        'type': 'situation',
                        'components': 'situation,question,options'
                    }
                else:  # 問題3
                    metadata = {
                        'video_id': video_id,
                        'section': section,
                        'type': 'action',
                        'components': 'action,question,options'
                    }
                
                questions.append({
                    'content': question,
                    'metadata': metadata
                })
                
            return questions
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return []

    def add_questions(self, structured_dir: str = "./structured") -> bool:
        """Add all structured questions to ChromaDB"""
        try:
            for file_path in Path(structured_dir).glob('*.txt'):
                questions = self.process_question_file(str(file_path))
                
                if not questions:
                    continue
                
                # Add to ChromaDB
                self.collection.add(
                    documents=[q['content'] for q in questions],
                    metadatas=[q['metadata'] for q in questions],
                    ids=[f"{q['metadata']['video_id']}_{q['metadata']['section']}_{i}" 
                         for i, q in enumerate(questions)]
                )
                
            return True
        except Exception as e:
            print(f"Error adding questions: {str(e)}")
            return False

    def query_questions(self, 
                       query_text: str, 
                       section_type: Optional[str] = None,
                       n_results: int = 3) -> List[Dict]:
        """Query questions with optional filters"""
        try:
            where = {"section": section_type} if section_type else None
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            
            return [{
                'question': doc,
                'metadata': meta,
                'id': id,
                'score': score
            } for doc, meta, id, score in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['ids'][0],
                results['distances'][0]
            )]
        except Exception as e:
            print(f"Error querying questions: {str(e)}")
            return []

def main():
    """Test the question store"""
    store = JLPTQuestionStore()
    
    # Add questions from structured files
    if store.add_questions():
        print("Questions added successfully")
        
        # Test query
        results = store.query_questions(
            "電車に乗ります。駅員に聞きます。",
            section_type="問題3"
        )
        
        for result in results:
            print(f"\nScore: {result['score']}")
            print(f"Question: {result['question']}")
            print(f"Metadata: {result['metadata']}")

if __name__ == "__main__":
    main()