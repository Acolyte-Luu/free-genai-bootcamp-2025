from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from agent import run_agent, get_results_by_handler

app = FastAPI(title="Song Vocabulary API")

class MessageRequest(BaseModel):
    message_request: str

class HandlerResponse(BaseModel):
    handler: str
    status: str
    message: str
    song_id: Optional[int] = None
    title: Optional[str] = None
    artist: Optional[str] = None

class Part(BaseModel):
    kanji: str
    romaji: List[str]

class VocabularyItem(BaseModel):
    kanji: str
    romaji: str
    english: str
    parts: List[Part]

class AgentResponse(BaseModel):
    status: str
    lyrics: Optional[str] = None
    vocabulary: Optional[List[VocabularyItem]] = None
    error: Optional[Dict[str, Any]] = None

@app.post("/api/agent", response_model=HandlerResponse)
async def get_lyrics(request: MessageRequest):
    """
    Start the process of finding lyrics and extracting vocabulary.
    Returns a handler that can be used to retrieve the results.
    """
    try:
        result = await run_agent(request.message_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/results/{handler_id}", response_model=AgentResponse)
async def get_results(handler_id: str):
    """
    Retrieve the results using a handler ID.
    """
    try:
        result = get_results_by_handler(handler_id)
        if result["status"] == "error":
            if "data" in result:
                return {
                    "status": "error",
                    "error": result["data"]
                }
            return {
                "status": "error",
                "error": {"message": result["message"]}
            }
        
        return {
            "status": "success",
            "lyrics": result["lyrics"],
            "vocabulary": result["vocabulary"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to Song Vocabulary API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True) 