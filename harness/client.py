"""
Provider-agnostic LLM API client for the Flaming Horse agent harness.

Supports XAI and MiniMax via LLM_PROVIDER environment variable.
Switch providers by setting LLM_PROVIDER=XAI or LLM_PROVIDER=MINIMAX.
"""

import os
import time
import json
from typing import Optional, Dict, Any
import requests


# Provider configuration defaults
PROVIDER_DEFAULTS = {
    "XAI": {
        "base_url": "https://api.x.ai/v1",
        "model": "grok-code-fast-1",
    },
    "MINIMAX": {
        "base_url": "https://api.minimax.io/v1",
        "model": "MiniMax-M2.5",
    },
}


class LLMClient:
    """Provider-agnostic LLM API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        """
        Initialize LLM client.

        Args:
            api_key: API key (auto-detected from provider if not set)
            model: Model to use (auto-detected from provider if not set)
            base_url: Base URL (auto-detected from provider if not set)
            provider: Provider name (XAI or MINIMAX, defaults to LLM_PROVIDER env var)
        """
        # Determine provider
        self.provider = (provider or os.getenv("LLM_PROVIDER", "XAI")).upper()
        if self.provider not in PROVIDER_DEFAULTS:
            raise ValueError(
                f"Unsupported provider: {self.provider}. "
                f"Supported: {', '.join(PROVIDER_DEFAULTS.keys())}"
            )

        # Get provider-specific env var prefix
        prefix = self.provider

        # API key: provider-specific key, with fallback to legacy XAI_API_KEY for XAI
        if api_key:
            self.api_key = api_key
        else:
            # Try provider-specific key first
            provider_key = os.getenv(f"{prefix}_API_KEY")
            if provider_key:
                self.api_key = provider_key
            elif self.provider == "XAI":
                # Fallback to legacy XAI_API_KEY for backward compatibility
                self.api_key = os.getenv("XAI_API_KEY")
                if not self.api_key:
                    raise ValueError(
                        f"{prefix}_API_KEY or XAI_API_KEY environment variable must be set"
                    )
            else:
                raise ValueError(f"{prefix}_API_KEY environment variable must be set")

        # Base URL: provider-specific URL, fallback to default
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = (
                os.getenv(f"{prefix}_BASE_URL")
                or PROVIDER_DEFAULTS[self.provider]["base_url"]
            )

        # Model: provider-specific model, fallback to provider default, then global AGENT_MODEL
        if model:
            self.model = model
        else:
            self.model = (
                os.getenv(f"{prefix}_MODEL")
                or PROVIDER_DEFAULTS[self.provider]["model"]
                or os.getenv("AGENT_MODEL")
            )

        # Strip provider prefix from model name if present (e.g., "xai/grok-..." → "grok-...")
        if self.model:
            self.model = self.model.removeprefix("xai/").removeprefix("minimax/")

        print(f"🤖 Harness using:")
        print(f"   Provider: {self.provider}")
        print(f"   Base URL: {self.base_url}")
        print(f"   Model: {self.model}")

        self.max_retries = 3
        self.retry_delay = 2.0

    def _make_request(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 16000,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Make a request to the LLM API.

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
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        url = f"{self.base_url}/chat/completions"

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=300,  # 5 minute timeout
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit - retry with exponential backoff
                    wait_time = self.retry_delay * (2**attempt)
                    print(f"⚠️  Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code >= 500:
                    wait_time = self.retry_delay * (2**attempt)
                    print(
                        f"⚠️  Server error {response.status_code}: {response.text[:500]}"
                    )
                    if attempt < self.max_retries - 1:
                        print(f"⚠️  Retrying after {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    response.raise_for_status()
                else:
                    print(f"❌ API error {response.status_code}: {response.text[:500]}")
                    response.raise_for_status()

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    print(
                        f"⚠️  Request timeout, retrying ({attempt + 1}/{self.max_retries})..."
                    )
                    time.sleep(self.retry_delay * (2**attempt))
                    continue
                else:
                    raise
            except requests.exceptions.RequestException as e:
                if (
                    isinstance(e, requests.exceptions.HTTPError)
                    and e.response is not None
                    and 400 <= e.response.status_code < 500
                    and e.response.status_code != 429
                ):
                    # Deterministic client-side errors should fail fast.
                    raise
                if attempt < self.max_retries - 1:
                    print(
                        f"⚠️  Request failed: {e}, retrying ({attempt + 1}/{self.max_retries})..."
                    )
                    time.sleep(self.retry_delay * (2**attempt))
                    continue
                else:
                    raise

        raise Exception(f"Failed to get response after {self.max_retries} attempts")

    def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 16000,
    ) -> str:
        """
        Get a chat completion from the LLM.

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
            {"role": "user", "content": user_prompt},
        ]

        response = self._make_request(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        # Extract the assistant's message
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]

        raise ValueError(f"Unexpected API response format: {response}")


def call_llm_api(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 16000,
) -> str:
    """
    Convenience function to call LLM API.

    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Response text from the model
    """
    client = LLMClient()
    return client.chat_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )


# Backward compatibility aliases
XAIClient = LLMClient
call_xai_api = call_llm_api


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
