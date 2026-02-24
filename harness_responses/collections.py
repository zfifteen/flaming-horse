"""
xAI Collections API integration for harness_responses.

Uses xai_sdk collections.search() and returns formatted reference chunks for prompt injection.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

DEFAULT_MANIM_COLLECTION_ID = "collection_096219fb-a4b3-41fc-bfb9-2f796cf5377b"
_MAX_RETRIES = 3
_RETRY_DELAY = 2.0
_MAX_FORMATTED_CHUNKS = 3
_MAX_CHARS_PER_CHUNK = 1800


@dataclass
class CollectionSearchResult:
    query: str
    collection_id: str
    limit: int
    chunks: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def hit_count(self) -> int:
        return len(self.chunks)

    @property
    def formatted_reference(self) -> str:
        if not self.chunks:
            return ""
        trimmed_chunks: list[str] = []
        for chunk in self.chunks[:_MAX_FORMATTED_CHUNKS]:
            if len(chunk) > _MAX_CHARS_PER_CHUNK:
                trimmed_chunks.append(chunk[:_MAX_CHARS_PER_CHUNK] + "\n[chunk truncated]")
            else:
                trimmed_chunks.append(chunk)
        formatted = "\n\n---\n\n".join(trimmed_chunks)
        return (
            "## Manim CE Reference Documentation\n\n"
            "The following was retrieved from the official Manim CE reference. "
            "Use ONLY syntax, classes, and methods documented here:\n\n"
            f"{formatted}"
        )


def _resolve_collection_id() -> str:
    return (
        os.getenv("XAI_COLLECTION_ID")
        or os.getenv("FLAMING_HORSE_COLLECTION_ID")
        or DEFAULT_MANIM_COLLECTION_ID
    )


def _extract_chunks(search_response: Any) -> list[str]:
    results = getattr(search_response, "results", None)
    if results is None:
        results = getattr(search_response, "matches", None)
    if results is None:
        return []

    chunks: list[str] = []
    for item in results:
        text = ""
        if isinstance(item, dict):
            text = (
                str(item.get("text", "")).strip()
                or str(item.get("chunk_content", "")).strip()
                or str(item.get("content", "")).strip()
            )
        else:
            text = (
                str(getattr(item, "text", "")).strip()
                or str(getattr(item, "chunk_content", "")).strip()
                or str(getattr(item, "content", "")).strip()
            )
        if text:
            chunks.append(text)
    return chunks


def search_manim_collection(query: str, limit: int = 10) -> CollectionSearchResult:
    """
    Search Manim reference collection and return a structured result.

    Never raises; fail-soft by returning a result with empty chunks and an error message.
    """
    collection_id = _resolve_collection_id()
    query = (query or "").strip()
    result = CollectionSearchResult(
        query=query,
        collection_id=collection_id,
        limit=limit,
    )
    if not query:
        result.error = "empty_query"
        return result

    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        result.error = "missing_api_key"
        print("⚠️  Collections search skipped: XAI_API_KEY not set")
        return result

    from xai_sdk.sync.client import Client

    client = Client(api_key=api_key)
    print("🔍 Retrieving Manim docs from Collections...")

    for attempt in range(_MAX_RETRIES):
        try:
            response = client.collections.search(
                query=query,
                collection_ids=[collection_id],
                limit=limit,
            )
            chunks = _extract_chunks(response)
            if not chunks:
                result.error = "no_results"
                print("⚠️  Collections search returned no results")
                return result
            result.chunks = chunks
            print(f"✅ Retrieved {len(chunks)} Manim documentation chunk(s)")
            return result
        except Exception as exc:
            err = str(exc)
            result.error = err
            err_lower = err.lower()
            is_transient = any(
                token in err_lower for token in ("timeout", "unavailable", "429", "503", "502")
            )
            if not is_transient or attempt == _MAX_RETRIES - 1:
                print(f"⚠️  Collections search failed: {err}")
                return result
            wait_time = _RETRY_DELAY * (2 ** attempt)
            print(
                f"⚠️  Collections search transient failure: {err}. "
                f"Retrying after {wait_time}s..."
            )
            time.sleep(wait_time)

    return result
