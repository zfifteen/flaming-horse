"""
xAI Collections API integration for Manim-aware scene generation.

Retrieves relevant Manim CE documentation chunks from the manim-reference
collection before each scene generation call.
"""

import os

import requests

COLLECTIONS_SEARCH_URL = "https://api.x.ai/v1/documents/search"
MANIM_COLLECTION_ID = "collection_096219fb-a4b3-41fc-bfb9-2f796cf5377b"


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

        payload = {
            "collection_ids": [MANIM_COLLECTION_ID],
            "query": query,
            "num_results": limit,
            "retrieval_mode": "hybrid",
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        print("🔍 Retrieving Manim docs for scene generation...")
        response = requests.post(
            COLLECTIONS_SEARCH_URL,
            headers=headers,
            json=payload,
            timeout=15,
        )

        if response.status_code != 200:
            print(
                f"⚠️  Collections search returned {response.status_code}: "
                f"{response.text[:200]}"
            )
            return ""

        data = response.json()
        results = data.get("results", [])

        if not results:
            print("⚠️  Collections search returned no results")
            return ""

        chunks = [
            item.get("text", "").strip()
            for item in results
            if item.get("text", "").strip()
        ]
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
