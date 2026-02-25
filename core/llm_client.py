"""
JCode LLM Client - Zhipu GLM-5 Integration

Provides a client for interacting with Zhipu GLM-5 model.
"""

import os
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass

# Try to import zhipuai, handle if not installed
try:
    from zhipuai import ZhipuAI
    ZHIPUAI_AVAILABLE = True
except ImportError:
    ZHIPUAI_AVAILABLE = False


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    api_key: Optional[str] = None
    model: str = "glm-4"  # Use glm-4 as default (glm-5 may not be available yet)
    temperature: float = 0.7
    max_tokens: int = 4096
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("ZHIPUAI_API_KEY")


class LLMClient:
    """
    LLM Client for Zhipu GLM models.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self._client = None
        
        if ZHIPUAI_AVAILABLE and self.config.api_key:
            self._client = ZhipuAI(api_key=self.config.api_key)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send chat messages and get response.
        """
        if not ZHIPUAI_AVAILABLE:
            raise ImportError("zhipuai is not installed. Run: pip install zhipuai")
        
        if not self._client:
            raise ValueError("API key not configured. Set ZHIPUAI_API_KEY environment variable.")
        
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens
        )
        
        return response.choices[0].message.content
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Generator[str, None, None]:
        """
        Send chat messages and stream response.
        """
        if not ZHIPUAI_AVAILABLE:
            raise ImportError("zhipuai is not installed. Run: pip install zhipuai")
        
        if not self._client:
            raise ValueError("API key not configured. Set ZHIPUAI_API_KEY environment variable.")
        
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def is_available(self) -> bool:
        """Check if LLM client is available."""
        return ZHIPUAI_AVAILABLE and self._client is not None


def create_llm_client(config: Optional[LLMConfig] = None) -> LLMClient:
    """Create an LLM client instance."""
    return LLMClient(config=config)


__all__ = ["LLMClient", "LLMConfig", "create_llm_client"]
