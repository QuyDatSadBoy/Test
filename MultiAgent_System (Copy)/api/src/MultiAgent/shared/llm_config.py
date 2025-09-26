from litellm import completion, acompletion
from api.core.config import settings
from langfuse import observe
import litellm
from typing import Optional

# Configure LiteLLM
litellm.set_verbose = settings.DEBUG

class LLMConfig:
    """LiteLLM configuration and wrapper"""
    
    def __init__(self):
        self.model = settings.LITELLM_MODEL
        self.base_url = settings.LITELLM_BASE_URL
        self.api_key = settings.LITELLM_API_KEY
        self.temperature = settings.LITELLM_TEMPERATURE
        self.max_tokens = settings.LITELLM_MAX_TOKENS
        self.model_provider = settings.LITELLM_MODEL_PROVIDER
        
        if self.base_url and self.api_key:
            litellm.api_base = self.base_url
            litellm.api_key = self.api_key

    @observe(name="llm_completion")
    async def complete(self, messages, user_id: Optional[str] = None, session_id: Optional[str] = None, **kwargs):
        """Async completion wrapper for LiteLLM proxy"""
        try:
            response = await acompletion(
                model=self.model,
                messages=messages,
                api_base=(self.base_url or "").rstrip("/") + "/v1",
                api_key=self.api_key,
                custom_llm_provider=self.model_provider,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                metadata={
                    "user_id": user_id,
                    "session_id": session_id
                },
                **kwargs
            )
            return response
        except Exception as e:
            print(f"LiteLLM completion error: {e}")
            raise

    @observe(name="llm_completion_sync")
    def complete_sync(self, messages, user_id: Optional[str] = None, session_id: Optional[str] = None, **kwargs):
        """Sync completion wrapper for LiteLLM proxy"""
        try:
            response = completion(
                model=self.model,
                messages=messages,
                api_base=self.base_url,
                api_key=self.api_key,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                metadata={
                    "user_id": user_id,
                    "session_id": session_id
                },
                **kwargs
            )
            return response
        except Exception as e:
            print(f"LiteLLM completion error: {e}")
            raise

# Global LLM instance
llm_config = LLMConfig()