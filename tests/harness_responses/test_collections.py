"""Unit tests for harness_responses Collections integration."""

from types import SimpleNamespace

import harness_responses.collections as hr_collections


def test_search_manim_collection_missing_api_key(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    result = hr_collections.search_manim_collection("Text animation")
    assert result.hit_count == 0
    assert result.error == "missing_api_key"


def test_search_manim_collection_uses_collection_override(monkeypatch):
    captured = {}

    class _FakeCollections:
        def search(self, *, query, collection_ids, limit):
            captured["query"] = query
            captured["collection_ids"] = collection_ids
            captured["limit"] = limit
            return SimpleNamespace(
                results=[SimpleNamespace(text="Use Text(...).set_max_width(...)")]
            )

    class _FakeClient:
        def __init__(self, *, api_key):
            captured["api_key"] = api_key
            self.collections = _FakeCollections()

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setenv("XAI_COLLECTION_ID", "collection_override")
    monkeypatch.setattr("xai_sdk.sync.client.Client", lambda api_key: _FakeClient(api_key=api_key))

    result = hr_collections.search_manim_collection("Text API", limit=5)
    assert result.collection_id == "collection_override"
    assert result.hit_count == 1
    assert "set_max_width" in result.formatted_reference
    assert captured["collection_ids"] == ["collection_override"]
    assert captured["limit"] == 5


def test_search_manim_collection_retries_transient_then_succeeds(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(hr_collections.time, "sleep", lambda *_: None)
    calls = {"n": 0}

    class _FakeCollections:
        def search(self, *, query, collection_ids, limit):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("503 unavailable")
            return SimpleNamespace(matches=[SimpleNamespace(chunk_content="VGroup(...).arrange(...)")])

    class _FakeClient:
        def __init__(self, *, api_key):
            self.collections = _FakeCollections()

    monkeypatch.setattr("xai_sdk.sync.client.Client", lambda api_key: _FakeClient(api_key=api_key))
    result = hr_collections.search_manim_collection("VGroup arrange")
    assert result.hit_count == 1
    assert calls["n"] == 2
