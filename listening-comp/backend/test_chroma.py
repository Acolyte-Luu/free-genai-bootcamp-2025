import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag import JLPTQuestionStore

def test_chroma():
    """Test direct insertion to ChromaDB"""
    print("Testing ChromaDB...")
    
    # Create store
    store = JLPTQuestionStore()
    
    # Print current collection status
    print(f"Current collection size: {len(store.collection.get()['ids'])}")
    
    # Try direct insertion
    try:
        print("Attempting direct insertion...")
        store.collection.add(
            documents=["Test document 1", "Test document 2", "Test document 3"],
            metadatas=[
                {"section": "問題1", "video_id": "test"},
                {"section": "問題2", "video_id": "test"},
                {"section": "問題3", "video_id": "test"}
            ],
            ids=["test_1", "test_2", "test_3"]
        )
        print(f"After insertion: {len(store.collection.get()['ids'])}")
        
        # Check results
        results = store.query_questions("Test document", n_results=3)
        print(f"Query results: {results}")
        return True
    except Exception as e:
        print(f"Error during direct insertion: {str(e)}")
        return False

if __name__ == "__main__":
    test_chroma() 