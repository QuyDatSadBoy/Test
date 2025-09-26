from langfuse import Langfuse, observe
from api.core.config import settings
from typing import Optional
import functools
import asyncio

# Initialize Langfuse
langfuse_client: Optional[Langfuse] = None

if settings.LANGFUSE_ENABLED and settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
    langfuse_client = Langfuse(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST
    )

def trace_llm_call(name: str = None):
    """Decorator to trace LLM calls with Langfuse"""
    def decorator(func):
        if not settings.LANGFUSE_ENABLED or not langfuse_client:
            return func
        
        @observe(name=name or func.__name__)
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract user_id and session_id from kwargs or request
            user_id = kwargs.get('user_id')
            session_id = kwargs.get('session_id')
            
            # If first argument is a request object, try to extract from it
            if args and hasattr(args[0], 'user_id'):
                user_id = getattr(args[0], 'user_id', user_id)
                session_id = getattr(args[0], 'session_id', session_id)
            
            # Update current trace with user context
            if user_id or session_id:
                langfuse_client.update_current_trace(
                    user_id=user_id,
                    session_id=session_id
                )
            
            return await func(*args, **kwargs)
        
        @observe(name=name or func.__name__)
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Extract user_id and session_id from kwargs or request
            user_id = kwargs.get('user_id')
            session_id = kwargs.get('session_id')
            
            # If first argument is a request object, try to extract from it
            if args and hasattr(args[0], 'user_id'):
                user_id = getattr(args[0], 'user_id', user_id)
                session_id = getattr(args[0], 'session_id', session_id)
            
            # Update current trace with user context
            if user_id or session_id:
                langfuse_client.update_current_trace(
                    user_id=user_id,
                    session_id=session_id
                )
            
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

def update_current_trace(user_id: Optional[str] = None, session_id: Optional[str] = None, **kwargs):
    """Update current trace with user_id and session_id"""
    if langfuse_client:
        langfuse_client.update_current_trace(
            user_id=user_id,
            session_id=session_id,
            **kwargs
        )

def flush_observations():
    """Flush pending observations to Langfuse"""
    if langfuse_client:
        langfuse_client.flush()