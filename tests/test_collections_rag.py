"""Tests for xAI Collections RAG integration in scene generation prompts."""

import json
from pathlib import Path

import requests

import harness.collections as collections_module
from harness.collections import search_manim_collection
from harness.prompts import compose_build_scenes_prompt, compose_scene_repair_prompt


class _CollectionsResp:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data if data is not None else {
            "results": [
                {"text": "VGroup arranges mobjects in a group."},
                {"text": "Text creates a text mobject."},
            ]
        }
        self.text = "ok"

    def json(self):
        return self._data


def _make_project(tmp_path: Path, scene_title: str = "Intro"):
    plan = {
        "title": "Test Video",
        "scenes": [
            {
                "id": "scene_01",
                "title": scene_title,
                "narration_key": "scene_01",
                "description": "Test scene description",
            }
        ],
    }
    (tmp_path / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
    (tmp_path / "narration_script.py").write_text(
        "SCRIPT = {'scene_01': 'This is the narration text for the scene.'}",
        encoding="utf-8",
    )
    (tmp_path / "scene_01.py").write_text("print('x')", encoding="utf-8")
    state = {
        "plan_file": "plan.json",
        "narration_file": "narration_script.py",
        "scenes": [
            {
                "id": "scene_01",
                "title": scene_title,
                "file": "scene_01.py",
                "narration_key": "scene_01",
            }
        ],
        "current_scene_index": 0,
    }
    return state, tmp_path


def test_search_manim_collection_returns_chunks(monkeypatch):
    """search_manim_collection returns formatted chunks on successful API call."""
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(
        collections_module.requests, "post", lambda *a, **kw: _CollectionsResp()
    )

    result = search_manim_collection("VGroup usage in Manim")

    assert "VGroup arranges mobjects in a group." in result
    assert "Text creates a text mobject." in result
    assert "Manim CE Reference Documentation" in result


def test_search_manim_collection_no_api_key(monkeypatch):
    """search_manim_collection returns empty string when XAI_API_KEY is not set."""
    monkeypatch.delenv("XAI_API_KEY", raising=False)

    result = search_manim_collection("VGroup usage")

    assert result == ""


def test_search_manim_collection_api_error(monkeypatch):
    """search_manim_collection returns empty string after exhausting retries on 5xx."""
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(collections_module.time, "sleep", lambda *_: None)
    monkeypatch.setattr(
        collections_module.requests,
        "post",
        lambda *a, **kw: _CollectionsResp(status_code=500, data={}),
    )

    result = search_manim_collection("VGroup usage")

    assert result == ""


def test_search_manim_collection_retries_then_succeeds(monkeypatch):
    """search_manim_collection retries on 429 and returns chunks on eventual success."""
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(collections_module.time, "sleep", lambda *_: None)
    calls = {"n": 0}
    chunk_text = "Create animates drawing a shape."

    def post_429_then_ok(*a, **kw):
        calls["n"] += 1
        if calls["n"] < 2:
            return _CollectionsResp(status_code=429, data={})
        return _CollectionsResp(data={"results": [{"text": chunk_text}]})

    monkeypatch.setattr(collections_module.requests, "post", post_429_then_ok)

    result = search_manim_collection("animation shapes")

    assert chunk_text in result
    assert calls["n"] == 2


def test_search_manim_collection_matches_format(monkeypatch):
    """search_manim_collection handles 'matches[].chunk_content' response shape."""
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    chunk_text = "MathTex renders LaTeX mathematics."
    monkeypatch.setattr(
        collections_module.requests,
        "post",
        lambda *a, **kw: _CollectionsResp(
            data={"matches": [{"chunk_content": chunk_text}]}
        ),
    )

    result = search_manim_collection("MathTex LaTeX")

    assert chunk_text in result
    assert "Manim CE Reference Documentation" in result


def test_search_manim_collection_empty_results(monkeypatch):
    """search_manim_collection returns empty string when results list is empty."""
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(
        collections_module.requests,
        "post",
        lambda *a, **kw: _CollectionsResp(data={"results": []}),
    )

    result = search_manim_collection("VGroup usage")

    assert result == ""


def test_search_manim_collection_request_exception(monkeypatch):
    """search_manim_collection returns empty string on network exception."""
    monkeypatch.setenv("XAI_API_KEY", "test-key")

    def raise_exc(*a, **kw):
        raise requests.exceptions.ConnectionError("network down")

    monkeypatch.setattr(collections_module.requests, "post", raise_exc)

    result = search_manim_collection("VGroup usage")

    assert result == ""


def test_compose_build_scenes_prompt_includes_collections_chunks(monkeypatch, tmp_path):
    """compose_build_scenes_prompt injects Collections chunks into the user prompt."""
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    chunk_text = "VGroup arranges mobjects in a group."
    monkeypatch.setattr(
        collections_module.requests,
        "post",
        lambda *a, **kw: _CollectionsResp(data={"results": [{"text": chunk_text}]}),
    )

    state, project_dir = _make_project(tmp_path)
    _, user_prompt = compose_build_scenes_prompt(state, project_dir)

    assert chunk_text in user_prompt
    assert "Manim CE Reference Documentation" in user_prompt


def test_compose_build_scenes_prompt_no_api_key_still_works(monkeypatch, tmp_path):
    """compose_build_scenes_prompt works even when XAI_API_KEY is not set."""
    monkeypatch.delenv("XAI_API_KEY", raising=False)

    state, project_dir = _make_project(tmp_path)
    _, user_prompt = compose_build_scenes_prompt(state, project_dir)

    assert isinstance(user_prompt, str)
    assert len(user_prompt) > 0


def test_compose_scene_repair_prompt_includes_collections_chunks(monkeypatch, tmp_path):
    """compose_scene_repair_prompt injects Collections chunks into the user prompt."""
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    chunk_text = "FadeIn animates a fade-in effect."
    monkeypatch.setattr(
        collections_module.requests,
        "post",
        lambda *a, **kw: _CollectionsResp(data={"results": [{"text": chunk_text}]}),
    )

    state, project_dir = _make_project(tmp_path)
    scene_file = project_dir / "scene_01.py"
    _, user_prompt = compose_scene_repair_prompt(
        state, project_dir, scene_file, "NameError: name 'FadeIn' is not defined"
    )

    assert chunk_text in user_prompt
    assert "Manim CE Reference Documentation" in user_prompt
