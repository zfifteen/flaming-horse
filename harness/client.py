"""
xAI API client for the Flaming Horse agent harness.

Provides direct integration with xAI's chat completions API,
bypassing OpenCode's overhead.
"""

import os
import time
import json
from typing import Optional, Dict, Any
import requests


class XAIClient:
    """Client for xAI API communication."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize xAI client.
        
        Args:
            api_key: xAI API key (defaults to XAI_API_KEY env var)
            model: Model to use (defaults to AGENT_MODEL env var or grok-2-1212)
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("XAI_API_KEY environment variable not set")
        
        self.model = model or os.getenv("AGENT_MODEL", "grok-2-1212")
        self.base_url = "https://api.x.ai/v1"
        self.max_retries = 3
        self.retry_delay = 2.0
    
    def _make_request(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 16000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Make a request to the xAI API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            API response as dict
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        url = f"{self.base_url}/chat/completions"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=300  # 5 minute timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit - retry with exponential backoff
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"⚠️  Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  Request timeout, retrying ({attempt + 1}/{self.max_retries})...")
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  Request failed: {e}, retrying ({attempt + 1}/{self.max_retries})...")
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise
        
        raise Exception(f"Failed to get response after {self.max_retries} attempts")
    
    def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 16000
    ) -> str:
        """
        Get a chat completion from xAI.
        
        Args:
            system_prompt: System prompt (instructions)
            user_prompt: User prompt (task/question)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response text from the model
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_request(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )
        
        # Extract the assistant's message
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
        
        raise ValueError(f"Unexpected API response format: {response}")


def call_xai_api(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 16000
) -> str:
    """
    Convenience function to call xAI API.
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Response text from the model
    """
    client = XAIClient()
    return client.chat_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )


def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count.
    
    Uses a simple heuristic: ~4 characters per token on average.
    For more accurate counting, could use tiktoken or similar.
    
    Args:
        text: Text to estimate
        
    Returns:
        Estimated token count
    """
    return len(text) // 4
