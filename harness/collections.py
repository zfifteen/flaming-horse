"""
xAI Collections API integration for Manim-aware scene generation.

Retrieves relevant Manim CE documentation chunks from the manim-reference
collection before each scene generation call.
"""

import os
import time

import requests

COLLECTIONS_SEARCH_URL = "https://api.x.ai/v1/documents/search"
DEFAULT_MANIM_COLLECTION_ID = "collection_096219fb-a4b3-41fc-bfb9-2f796cf5377b"

_MAX_RETRIES = 3
_RETRY_DELAY = 2.0


def search_manim_collection(query: str, limit: int = 8) -> str:
    """Search the manim-reference collection and return formatted documentation chunks.

    Returns relevant Manim CE API documentation as a formatted string to inject
    into scene generation prompts.  Never raises; returns empty string on failure.

    Args:
        query: Search query (scene details or error context).
        limit: Maximum number of result chunks to retrieve.

    Returns:
        Formatted reference section string, or empty string on any failure.
    """
    try:
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            print("⚠️  Collections search skipped: XAI_API_KEY not set")
            return ""

        collection_id = (
            os.getenv("XAI_COLLECTION_ID")
            or os.getenv("FLAMING_HORSE_COLLECTION_ID")
            or DEFAULT_MANIM_COLLECTION_ID
        )

        payload = {
            "query": query,
            "source": {
                "collection_ids": [collection_id],
            },
            "num_results": limit,
            "retrieval_mode": {"type": "hybrid"},
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        print("🔍 Retrieving Manim docs for scene generation...")
        response = None
        for attempt in range(_MAX_RETRIES):
            try:
                response = requests.post(
                    COLLECTIONS_SEARCH_URL,
                    headers=headers,
                    json=payload,
                    timeout=15,
                )
            except requests.exceptions.RequestException as e:
                wait_time = _RETRY_DELAY * (2**attempt)
                if attempt < _MAX_RETRIES - 1:
                    print(
                        f"⚠️  Collections search request failed: {e}. "
                        f"Retrying after {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                print(
                    f"⚠️  Collections search request failed after {_MAX_RETRIES} "
                    f"attempts: {e}"
                )
                return ""
            if response.status_code == 200:
                break
            elif response.status_code == 429 or response.status_code >= 500:
                wait_time = _RETRY_DELAY * (2**attempt)
                if attempt < _MAX_RETRIES - 1:
                    print(
                        f"⚠️  Collections search {response.status_code}, "
                        f"retrying after {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    print(
                        f"⚠️  Collections search returned {response.status_code} "
                        f"after {_MAX_RETRIES} attempts"
                    )
                    return ""
            else:
                print(
                    f"⚠️  Collections search returned {response.status_code}: "
                    f"{response.text[:200]}"
                )
                return ""

        if response is None or response.status_code != 200:
            return ""

        data = response.json()
        # Handle both "results[].text" and "matches[].chunk_content" response shapes
        results = data.get("results", data.get("matches", []))

        if not results:
            print("⚠️  Collections search returned no results")
            return ""

        chunks = []
        for item in results:
            text = (item.get("text") or item.get("chunk_content", "")).strip()
            if text:
                chunks.append(text)

        if not chunks:
            return ""

        print(f"✅ Retrieved {len(chunks)} Manim documentation chunk(s)")
        formatted = "\n\n---\n\n".join(chunks)
        return (
            "## Manim CE Reference Documentation\n\n"
            "The following was retrieved from the official Manim CE reference. "
            "Use ONLY syntax, classes, and methods documented here:\n\n"
            f"{formatted}"
        )

    except Exception as e:
        print(f"⚠️  Collections search failed: {e}")
        return ""
