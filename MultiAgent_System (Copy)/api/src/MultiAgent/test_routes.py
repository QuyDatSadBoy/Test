from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .shared.llm_config import llm_config
from .shared.observability import trace_llm_call, update_current_trace, flush_observations
import uuid
import logging

router = APIRouter(prefix="/test", tags=["test"])

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
@trace_llm_call("test_chat_endpoint")
async def test_chat(request: ChatRequest):
    """Test endpoint to verify Langfuse tracing with user_id and session_id"""
    
    try:
        # Generate IDs if not provided
        user_id = request.user_id or f"test_user_{uuid.uuid4().hex[:8]}"
        session_id = request.session_id or f"test_session_{uuid.uuid4().hex[:8]}"
        
        # Update current trace with user context
        update_current_trace(user_id=user_id, session_id=session_id)
        
        # Call LLM with tracing
        messages = [{"role": "user", "content": request.message}]
        
        response = await llm_config.complete(
            messages=messages,
            user_id=user_id,
            session_id=session_id
        )
        
        # Flush observations to ensure they're sent to Langfuse
        flush_observations()
        
        return ChatResponse(
            response=response.choices[0].message.content,
            user_id=user_id,
            session_id=session_id
        )
        
    except Exception as e:
        logging.error(f"Full error: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "ok", "message": "MultiAgent system is running"}

@router.get("/debug/litellm")
@trace_llm_call("debug_litellm")
async def debug_litellm():
    """Debug LiteLLM connection"""
    try:
        test_messages = [{"role": "user", "content": "Hello, this is a test"}]
        response = await llm_config.complete(test_messages)
        return {
            "status": "success", 
            "response": response.choices[0].message.content,
            "model": llm_config.model,
            "base_url": llm_config.base_url
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "model": llm_config.model,
            "base_url": llm_config.base_url
        }