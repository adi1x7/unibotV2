"""
FastAPI server for UniBot frontend
Run this instead of app.py when using the custom frontend
"""
import sys
from pathlib import Path

# Add parent directory to path to import UniBot modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import os
from dotenv import load_dotenv
from sidekick import UniBot

load_dotenv(override=True)

app = FastAPI(title="UniBot API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global UniBot instance
unibot: Optional[UniBot] = None

class MessageRequest(BaseModel):
    message: str
    success_criteria: Optional[str] = None
    history: Optional[List[Dict[str, Any]]] = None

class MessageResponse(BaseModel):
    response: str
    history: List[Dict[str, Any]]
    status: str

@app.on_event("startup")
async def startup_event():
    """Initialize UniBot on server startup"""
    global unibot
    try:
        college_url = os.getenv("COLLEGE_WEBSITE_URL", None)
        unibot = UniBot(college_website_url=college_url)
        await unibot.setup()
        print("✅ UniBot initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing UniBot: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    global unibot
    if unibot:
        try:
            unibot.cleanup()
        except Exception as e:
            print(f"Error during cleanup: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "UniBot API",
        "unibot_ready": unibot is not None
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "unibot_ready": unibot is not None
    }

def filter_feedback_messages(history):
    """Remove evaluator feedback messages from history"""
    if not history:
        return history
    filtered = []
    for msg in history:
        content = msg.get("content", "") if isinstance(msg, dict) else ""
        if "Evaluator Feedback" not in str(content):
            filtered.append(msg)
    return filtered

@app.post("/api/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """Handle chat messages"""
    global unibot
    
    if not unibot:
        raise HTTPException(status_code=503, detail="UniBot not initialized")
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Filter existing feedback from history
        history = filter_feedback_messages(request.history or [])
        
        # Process message
        success_criteria = request.success_criteria or "The answer should be clear and accurate"
        updated_history = await unibot.run_superstep(
            request.message,
            success_criteria,
            history
        )
        
        # Filter feedback from results
        updated_history = filter_feedback_messages(updated_history)
        
        # Get the last assistant message (skip evaluator feedback)
        assistant_messages = [
            msg for msg in updated_history 
            if msg.get("role") == "assistant" and 
            "Evaluator Feedback" not in str(msg.get("content", ""))
        ]
        
        if assistant_messages:
            response_text = assistant_messages[-1].get("content", "")
        else:
            response_text = "I apologize, but I encountered an issue processing your request."
        
        return MessageResponse(
            response=response_text,
            history=updated_history,
            status="success"
        )
        
    except Exception as e:
        print(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.post("/api/reset")
async def reset():
    """Reset the UniBot instance"""
    global unibot
    
    try:
        if unibot:
            unibot.cleanup()
        
        college_url = os.getenv("COLLEGE_WEBSITE_URL", None)
        unibot = UniBot(college_website_url=college_url)
        await unibot.setup()
        
        return {"status": "success", "message": "UniBot reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting UniBot: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

