"""
Tests for harness_responses plan phase.

Covers:
  - Pydantic schema validation (pass/fail)
  - Semantic validation (duration bounds and content quality)
  - Artifact write (plan.json format and IDs)
  - CLI module invocation and dry-run
  - Prompt composition
  - Legacy harness unaffected
"""

import json
import runpy
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

import harness_responses.cli as hr_cli
import harness_responses.client as hr_client
import harness_responses.parser as hr_parser
import harness_responses.prompts as hr_prompts
from harness_responses.collections import CollectionSearchResult
from harness_responses.schemas.build_scenes import BuildScenesResponse
from harness_responses.schemas.narration import NarrationResponse
from harness_responses.schemas.plan import PlanResponse, SceneItem
from harness_responses.schemas.scene_qc import SceneQcResponse
from harness_responses.schemas.scene_repair import SceneRepairResponse
from harness_responses.parser import SemanticValidationError
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_valid_scene(idx: int = 0) -> SceneItem:
    return SceneItem(
        title=f"Scene {idx + 1}",
        description=f"Description for scene {idx + 1}",
        estimated_duration_seconds=30,
        visual_ideas=["visual A", "visual B"],
    )


def _make_valid_plan(scene_count: int = 9) -> PlanResponse:
    return PlanResponse(
        title="Test Video",
        description="A test video about testing",
        target_duration_seconds=300,
        scenes=[_make_valid_scene(i) for i in range(scene_count)],
    )


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    state = {"phase": "plan", "scenes": [], "current_scene_index": 0}
    (project / "project_state.json").write_text(json.dumps(state), encoding="utf-8")
    return project


def _make_scene_project(tmp_path: Path) -> Path:
    project = tmp_path / "scene_project"
    project.mkdir()
    state = {
        "phase": "build_scenes",
        "plan_file": "plan.json",
        "narration_file": "narration_script.py",
        "scenes": [
            {
                "id": "scene_01",
                "title": "Scene 1",
                "narration_key": "scene_01",
                "file": "scene_01.py",
                "class_name": "Scene01",
            }
        ],
        "current_scene_index": 0,
    }
    (project / "project_state.json").write_text(json.dumps(state), encoding="utf-8")
    (project / "plan.json").write_text(
        json.dumps(
            {
                "title": "Plan",
                "description": "desc",
                "target_duration_seconds": 300,
                "scenes": [
                    {
                        "id": "scene_01",
                        "narration_key": "scene_01",
                        "title": "Scene 1",
                        "description": "desc",
                        "estimated_duration_seconds": 30,
                        "visual_ideas": ["idea"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (project / "narration_script.py").write_text(
        "SCRIPT = {\n    \"scene_01\": \"Narration text for scene one.\"\n}\n",
        encoding="utf-8",
    )
    (project / "scene_01.py").write_text(
        "from manim import *\n\n"
        "class Scene01(VoiceoverScene):\n"
        "    def construct(self):\n"
        "        with self.voiceover(text=SCRIPT[\"scene_01\"]) as tracker:\n"
        "            # SLOT_START:scene_body\n"
        "            title = Text(\"Placeholder\")\n"
        "            self.play(Write(title), run_time=min(1.0, tracker.duration * 0.2))\n"
        "            # SLOT_END:scene_body\n",
        encoding="utf-8",
    )
    return project


def _make_narration_project(tmp_path: Path) -> Path:
    project = tmp_path / "narration_project"
    project.mkdir()
    state = {
        "phase": "narration",
        "plan_file": "plan.json",
        "scenes": [{"id": "scene_01", "narration_key": "scene_01", "title": "Scene 1"}],
        "current_scene_index": 0,
    }
    (project / "project_state.json").write_text(json.dumps(state), encoding="utf-8")
    (project / "plan.json").write_text(
        json.dumps(
            {
                "title": "Narration Test",
                "description": "desc",
                "target_duration_seconds": 300,
                "scenes": [
                    {
                        "id": "scene_01",
                        "narration_key": "scene_01",
                        "title": "Scene 1",
                        "description": "desc",
                        "estimated_duration_seconds": 30,
                        "visual_ideas": ["idea"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return project


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------

class TestPlanSchema:
    def test_valid_plan_parses(self):
        plan = _make_valid_plan()
        assert plan.title == "Test Video"
        assert len(plan.scenes) == 9

    def test_schema_allows_empty_title_semantics_enforce_non_empty(self):
        plan = PlanResponse(
            title="",
            description="desc",
            target_duration_seconds=300,
            scenes=[_make_valid_scene(i) for i in range(9)],
        )
        assert plan.title == ""

    def test_schema_allows_empty_visual_ideas_semantics_enforce_non_empty(self):
        scene = SceneItem(
            title="Scene",
            description="desc",
            estimated_duration_seconds=30,
            visual_ideas=[],
        )
        assert scene.visual_ideas == []

    def test_schema_enforces_duration_bounds(self):
        with pytest.raises(ValidationError):
            PlanResponse(
                title="Test",
                description="desc",
                target_duration_seconds=0,
                scenes=[_make_valid_scene(i) for i in range(9)],
            )
        with pytest.raises(ValidationError):
            SceneItem(
                title="Bad scene",
                description="desc",
                estimated_duration_seconds=0,
                visual_ideas=["idea"],
            )


# ---------------------------------------------------------------------------
# Semantic validation tests
# ---------------------------------------------------------------------------

class TestSemanticValidation:
    def test_valid_plan_passes(self, tmp_path):
        project = _make_project(tmp_path)
        plan = _make_valid_plan(9)
        result = hr_parser.validate_and_write_plan(plan, project)
        assert result is True

    def test_plan_json_written(self, tmp_path):
        project = _make_project(tmp_path)
        plan = _make_valid_plan(9)
        hr_parser.validate_and_write_plan(plan, project)
        plan_path = project / "plan.json"
        assert plan_path.exists()
        data = json.loads(plan_path.read_text())
        assert data["title"] == "Test Video"
        assert len(data["scenes"]) == 9

    def test_plan_scenes_have_assigned_ids(self, tmp_path):
        project = _make_project(tmp_path)
        plan = _make_valid_plan(9)
        hr_parser.validate_and_write_plan(plan, project)
        data = json.loads((project / "plan.json").read_text())
        assert data["scenes"][0]["id"] == "scene_01"
        assert data["scenes"][0]["narration_key"] == "scene_01"
        assert data["scenes"][8]["id"] == "scene_09"

    def test_few_scenes_allowed(self, tmp_path):
        project = _make_project(tmp_path)
        plan = PlanResponse.model_construct(
            title="Test Video",
            description="A test video about testing",
            target_duration_seconds=300,
            scenes=[_make_valid_scene(i) for i in range(7)],
        )
        assert hr_parser.validate_and_write_plan(plan, project) is True

    def test_many_scenes_allowed(self, tmp_path):
        project = _make_project(tmp_path)
        plan = PlanResponse.model_construct(
            title="Test Video",
            description="A test video about testing",
            target_duration_seconds=300,
            scenes=[_make_valid_scene(i) for i in range(13)],
        )
        assert hr_parser.validate_and_write_plan(plan, project) is True

    def test_short_total_duration_allowed(self, tmp_path):
        project = _make_project(tmp_path)
        plan = PlanResponse.model_construct(
            title="Test",
            description="desc",
            target_duration_seconds=90,
            scenes=[_make_valid_scene(i) for i in range(3)],
        )
        assert hr_parser.validate_and_write_plan(plan, project) is True

    def test_short_scene_duration_allowed(self, tmp_path):
        project = _make_project(tmp_path)
        scenes = [_make_valid_scene(i) for i in range(3)]
        scenes[1] = SceneItem.model_construct(
            title="Short scene",
            description="desc",
            estimated_duration_seconds=5,
            visual_ideas=["idea"],
        )
        plan = PlanResponse.model_construct(
            title="Test",
            description="desc",
            target_duration_seconds=90,
            scenes=scenes,
        )
        assert hr_parser.validate_and_write_plan(plan, project) is True

    def test_empty_title_fails(self, tmp_path):
        project = _make_project(tmp_path)
        plan = PlanResponse(
            title="  ",
            description="desc",
            target_duration_seconds=300,
            scenes=[_make_valid_scene(i) for i in range(9)],
        )
        with pytest.raises(SemanticValidationError, match="title must not be empty"):
            hr_parser.validate_and_write_plan(plan, project)

    def test_failure_diagnostic_written(self, tmp_path):
        project = _make_project(tmp_path)
        plan = PlanResponse.model_construct(
            title="   ",
            description="A test video about testing",
            target_duration_seconds=300,
            scenes=[_make_valid_scene(i) for i in range(7)],
        )
        with pytest.raises(SemanticValidationError):
            hr_parser.validate_and_write_plan(plan, project, raw_response=None)
        diag = project / "log" / "responses_last_response.json"
        assert diag.exists()
        data = json.loads(diag.read_text())
        assert "validation_error" in data


class TestResponsesClient:
    class _DummySchema(BaseModel):
        ok: str

    class _FakeChat:
        def __init__(self, raw_content: str, outer):
            self.raw_content = raw_content
            self.outer = outer

        def append(self, msg):
            self.outer.setdefault("appended_messages", []).append(msg)
            return None

        def sample(self):
            response = _MockResponse(self.raw_content)
            response.id = self.outer.get("response_id", "mock_response_id_123")
            return response

    class _FakeChatFactory:
        def __init__(self, outer):
            self.outer = outer

        def create(self, model, **kwargs):
            self.outer["model"] = model
            self.outer["kwargs"] = kwargs
            raw_content = self.outer.get("raw_content", "{\"ok\":\"yes\"}")
            return TestResponsesClient._FakeChat(raw_content, self.outer)

    class _FakeClient:
        def __init__(self, *, api_key, _capture):
            _capture["api_key"] = api_key
            self.chat = TestResponsesClient._FakeChatFactory(_capture)

    class _FakeHttpResponse:
        def __init__(self, payload: dict):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def test_enable_web_search_wires_search_parameters(self, monkeypatch):
        capture = {}
        monkeypatch.setenv("XAI_API_KEY", "test-key")
        monkeypatch.setattr(
            "xai_sdk.sync.client.Client",
            lambda api_key: TestResponsesClient._FakeClient(api_key=api_key, _capture=capture),
        )
        monkeypatch.setattr("xai_sdk.chat.system", lambda s: {"role": "system", "content": s})
        monkeypatch.setattr("xai_sdk.chat.user", lambda s: {"role": "user", "content": s})

        raw, parsed = hr_client.call_responses_api(
            system_prompt="sys",
            user_prompt="usr",
            schema=self._DummySchema,
            enable_web_search=True,
        )
        assert parsed.ok == "yes"
        assert raw.id == "mock_response_id_123"
        assert "search_parameters" in capture["kwargs"]
        assert capture["kwargs"]["search_parameters"].mode == "on"
        assert capture["kwargs"]["response_format"] == "json_object"
        assert capture["kwargs"]["store_messages"] is True

    def test_disable_web_search_omits_search_parameters(self, monkeypatch):
        capture = {}
        monkeypatch.setenv("XAI_API_KEY", "test-key")
        monkeypatch.setattr(
            "xai_sdk.sync.client.Client",
            lambda api_key: TestResponsesClient._FakeClient(api_key=api_key, _capture=capture),
        )
        monkeypatch.setattr("xai_sdk.chat.system", lambda s: {"role": "system", "content": s})
        monkeypatch.setattr("xai_sdk.chat.user", lambda s: {"role": "user", "content": s})

        _, parsed = hr_client.call_responses_api(
            system_prompt="sys",
            user_prompt="usr",
            schema=self._DummySchema,
            enable_web_search=False,
        )
        assert parsed.ok == "yes"
        assert "search_parameters" not in capture["kwargs"]
        assert capture["kwargs"]["response_format"] == "json_object"
        assert capture["kwargs"]["store_messages"] is True
        assert "previous_response_id" not in capture["kwargs"]
        assert len(capture["appended_messages"]) == 2

    def test_previous_response_id_used_when_session_pointer_exists(
        self, monkeypatch, tmp_path
    ):
        capture = {}
        session_state = tmp_path / "responses_session.json"
        session_state.write_text(
            json.dumps(
                {
                    "model": "grok-4-1-fast",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                    "last_response_id": "resp_prev_001",
                    "phase": "plan",
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("XAI_API_KEY", "test-key")
        monkeypatch.setattr(
            "xai_sdk.sync.client.Client",
            lambda api_key: TestResponsesClient._FakeClient(api_key=api_key, _capture=capture),
        )
        monkeypatch.setattr("xai_sdk.chat.system", lambda s: {"role": "system", "content": s})
        monkeypatch.setattr("xai_sdk.chat.user", lambda s: {"role": "user", "content": s})

        raw, parsed = hr_client.call_responses_api(
            system_prompt="sys",
            user_prompt="usr",
            schema=self._DummySchema,
            session_state_path=session_state,
            phase="plan",
        )
        assert parsed.ok == "yes"
        assert capture["kwargs"]["previous_response_id"] == "resp_prev_001"
        assert getattr(raw, "previous_response_id_used") == "resp_prev_001"
        assert len(capture["appended_messages"]) == 2

    def test_session_state_stores_last_response_id_not_history(self, monkeypatch, tmp_path):
        capture = {"response_id": "resp_new_001"}
        session_state = tmp_path / "responses_session.json"
        monkeypatch.setenv("XAI_API_KEY", "test-key")
        monkeypatch.setattr(
            "xai_sdk.sync.client.Client",
            lambda api_key: TestResponsesClient._FakeClient(api_key=api_key, _capture=capture),
        )
        monkeypatch.setattr("xai_sdk.chat.system", lambda s: {"role": "system", "content": s})
        monkeypatch.setattr("xai_sdk.chat.user", lambda s: {"role": "user", "content": s})

        _, parsed = hr_client.call_responses_api(
            system_prompt="sys",
            user_prompt="usr",
            schema=self._DummySchema,
            session_state_path=session_state,
            phase="narration",
        )
        assert parsed.ok == "yes"

        data = json.loads(session_state.read_text(encoding="utf-8"))
        assert data["last_response_id"] == "resp_new_001"
        assert data["model"] == "grok-4-1-fast"
        assert data["phase"] == "narration"
        assert "history" not in data

    def test_build_scenes_with_phase_chain_sends_user_only(self, monkeypatch, tmp_path):
        capture = {}
        session_state = tmp_path / "responses_session.json"
        session_state.write_text(
            json.dumps(
                {
                    "model": "grok-4-1-fast",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                    "last_response_id": "resp_prev_build_001",
                    "phase": "build_scenes",
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("XAI_API_KEY", "test-key")
        monkeypatch.setattr(
            "xai_sdk.sync.client.Client",
            lambda api_key: TestResponsesClient._FakeClient(api_key=api_key, _capture=capture),
        )
        monkeypatch.setattr("xai_sdk.chat.system", lambda s: {"role": "system", "content": s})
        monkeypatch.setattr("xai_sdk.chat.user", lambda s: {"role": "user", "content": s})

        _, parsed = hr_client.call_responses_api(
            system_prompt="sys",
            user_prompt="usr",
            schema=self._DummySchema,
            session_state_path=session_state,
            phase="build_scenes",
        )

        assert parsed.ok == "yes"
        assert capture["kwargs"]["previous_response_id"] == "resp_prev_build_001"
        assert len(capture["appended_messages"]) == 1
        assert capture["appended_messages"][0]["role"] == "user"

    def test_build_scenes_without_chain_sends_system_and_user(self, monkeypatch, tmp_path):
        capture = {}
        session_state = tmp_path / "responses_session.json"
        monkeypatch.setenv("XAI_API_KEY", "test-key")
        monkeypatch.setattr(
            "xai_sdk.sync.client.Client",
            lambda api_key: TestResponsesClient._FakeClient(api_key=api_key, _capture=capture),
        )
        monkeypatch.setattr("xai_sdk.chat.system", lambda s: {"role": "system", "content": s})
        monkeypatch.setattr("xai_sdk.chat.user", lambda s: {"role": "user", "content": s})

        _, parsed = hr_client.call_responses_api(
            system_prompt="sys",
            user_prompt="usr",
            schema=self._DummySchema,
            session_state_path=session_state,
            phase="build_scenes",
        )

        assert parsed.ok == "yes"
        assert "previous_response_id" not in capture["kwargs"]
        assert len(capture["appended_messages"]) == 2
        assert capture["appended_messages"][0]["role"] == "system"
        assert capture["appended_messages"][1]["role"] == "user"

    def test_ensure_build_scenes_template_file_upload_once_then_reuse(
        self, monkeypatch, tmp_path
    ):
        template_file = tmp_path / "template.md"
        template_file.write_text("template body", encoding="utf-8")
        monkeypatch.setattr(hr_client, "_BUILD_SCENES_TEMPLATE_PATH", template_file)
        monkeypatch.setenv("XAI_API_KEY", "test-key")

        calls = {"count": 0}

        def _fake_post(*args, **kwargs):
            calls["count"] += 1
            return TestResponsesClient._FakeHttpResponse({"id": "file_abc123"})

        monkeypatch.setattr(hr_client.requests, "post", _fake_post)
        session_state = tmp_path / "responses_session.json"

        first = hr_client.ensure_build_scenes_template_file(
            session_state_path=session_state
        )
        second = hr_client.ensure_build_scenes_template_file(
            session_state_path=session_state
        )

        assert first["template_file_id"] == "file_abc123"
        assert first["uploaded"] is True
        assert second["template_file_id"] == "file_abc123"
        assert second["uploaded"] is False
        assert calls["count"] == 1

    def test_malformed_json_raises(self, monkeypatch):
        capture = {"raw_content": "{bad json"}
        monkeypatch.setenv("XAI_API_KEY", "test-key")
        monkeypatch.setattr(
            "xai_sdk.sync.client.Client",
            lambda api_key: TestResponsesClient._FakeClient(api_key=api_key, _capture=capture),
        )
        monkeypatch.setattr("xai_sdk.chat.system", lambda s: {"role": "system", "content": s})
        monkeypatch.setattr("xai_sdk.chat.user", lambda s: {"role": "user", "content": s})

        with pytest.raises(ValueError, match="Structured JSON validation failed"):
            hr_client.call_responses_api(
                system_prompt="sys",
                user_prompt="usr",
                schema=self._DummySchema,
                enable_web_search=False,
            )

    def test_schema_invalid_json_raises(self, monkeypatch):
        capture = {"raw_content": "{\"missing_ok\": true}"}
        monkeypatch.setenv("XAI_API_KEY", "test-key")
        monkeypatch.setattr(
            "xai_sdk.sync.client.Client",
            lambda api_key: TestResponsesClient._FakeClient(api_key=api_key, _capture=capture),
        )
        monkeypatch.setattr("xai_sdk.chat.system", lambda s: {"role": "system", "content": s})
        monkeypatch.setattr("xai_sdk.chat.user", lambda s: {"role": "user", "content": s})

        with pytest.raises(ValueError, match="Structured JSON validation failed"):
            hr_client.call_responses_api(
                system_prompt="sys",
                user_prompt="usr",
                schema=self._DummySchema,
                enable_web_search=False,
            )

    def test_write_phase_artifacts_plan(self, tmp_path):
        project = _make_project(tmp_path)
        plan = _make_valid_plan(9)
        assert hr_parser.write_phase_artifacts("plan", plan, project) is True

    def test_write_phase_artifacts_unimplemented_phase_raises(self, tmp_path):
        project = _make_project(tmp_path)
        with pytest.raises(NotImplementedError):
            hr_parser.write_phase_artifacts("review", None, project)

    def test_write_phase_artifacts_build_scenes(self, tmp_path):
        project = _make_scene_project(tmp_path)
        parsed = BuildScenesResponse(
            scene_body='title = Text("Rebuilt")\nself.play(Write(title), run_time=min(1.0, tracker.duration * 0.2))'
        )
        assert hr_parser.write_phase_artifacts("build_scenes", parsed, project) is True
        content = (project / "scene_01.py").read_text(encoding="utf-8")
        assert "Rebuilt" in content

    def test_write_phase_artifacts_scene_repair(self, tmp_path):
        project = _make_scene_project(tmp_path)
        parsed = SceneRepairResponse(
            scene_body='title = Text("Fixed")\nself.play(Write(title), run_time=min(1.0, tracker.duration * 0.2))'
        )
        assert hr_parser.write_phase_artifacts("scene_repair", parsed, project) is True
        content = (project / "scene_01.py").read_text(encoding="utf-8")
        assert "Fixed" in content

    def test_write_phase_artifacts_narration(self, tmp_path):
        project = _make_narration_project(tmp_path)
        parsed = NarrationResponse(script={"scene_01": "Hello narration"})
        assert hr_parser.write_phase_artifacts("narration", parsed, project) is True
        content = (project / "narration_script.py").read_text(encoding="utf-8")
        assert '"scene_01": "Hello narration"' in content

    def test_write_phase_artifacts_scene_qc(self, tmp_path):
        project = _make_scene_project(tmp_path)
        parsed = SceneQcResponse(report_markdown="# Scene QC Report\n\nAll good.")
        assert hr_parser.write_phase_artifacts("scene_qc", parsed, project) is True
        content = (project / "scene_qc_report.md").read_text(encoding="utf-8")
        assert "Scene QC Report" in content


# ---------------------------------------------------------------------------
# Prompt composition tests
# ---------------------------------------------------------------------------

class TestPromptComposition:
    def test_plan_prompts_load(self):
        system, user = hr_prompts.compose_prompt(
            phase="plan",
            topic="black holes",
            project_dir=Path("."),
        )
        assert "Manim" in system
        assert "black holes" in user

    def test_unknown_phase_raises(self, tmp_path):
        with pytest.raises(ValueError, match="not implemented"):
            hr_prompts.compose_prompt(
                phase="training",
                topic="test",
                project_dir=tmp_path,
            )

    def test_retry_context_appended(self):
        _, user = hr_prompts.compose_prompt(
            phase="plan",
            topic="test",
            retry_context="previous error details",
            project_dir=Path("."),
        )
        assert "previous error details" in user

    def test_no_retry_context_clean(self):
        _, user = hr_prompts.compose_prompt(
            phase="plan",
            topic="test",
            retry_context="",
            project_dir=Path("."),
        )
        assert "Retry context" not in user

    def test_build_scenes_prompt_loads(self, monkeypatch, tmp_path):
        project = _make_scene_project(tmp_path)
        captured = {}

        def _fake_search(query):
            captured["query"] = query
            return CollectionSearchResult(
                query=query,
                collection_id="collection_test",
                limit=10,
                chunks=["Text API docs"],
            )

        monkeypatch.setattr(
            hr_prompts,
            "search_manim_collection",
            _fake_search,
        )
        system, user = hr_prompts.compose_prompt(
            phase="build_scenes",
            project_dir=project,
        )
        assert "Build Scenes Phase" in system
        assert "Scene ID: scene_01" in user
        info = hr_prompts.consume_last_retrieval_info()
        assert info["phase"] == "build_scenes"
        assert "Phase: build_scenes" in captured["query"]
        assert "Video Production Agent - Build Scenes Phase" in captured["query"]
        assert "Scene ID:" not in captured["query"]
        assert "Narration key:" not in captured["query"]
        assert "Scene title:" not in captured["query"]
        assert "Current scene source:" in captured["query"]
        assert "class Scene01(VoiceoverScene):" in captured["query"]

    def test_build_scenes_first_scene_calls_collections(self, monkeypatch, tmp_path):
        project = _make_scene_project(tmp_path)
        calls = {"count": 0}

        def _fake_search(query, limit=10):
            calls["count"] += 1
            return CollectionSearchResult(
                query=query,
                collection_id="collection_test",
                limit=limit,
                chunks=["Text API docs"],
            )

        monkeypatch.setattr(hr_prompts, "search_manim_collection", _fake_search)

        _, user = hr_prompts.compose_prompt(
            phase="build_scenes",
            project_dir=project,
        )

        assert calls["count"] == 1
        assert "Manim CE Reference Documentation" in user

    def test_build_scenes_non_first_scene_skips_collections(self, monkeypatch, tmp_path):
        project = _make_scene_project(tmp_path)
        state_path = project / "project_state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["scenes"].append(
            {
                "id": "scene_02",
                "title": "Scene 2",
                "narration_key": "scene_02",
                "file": "scene_02.py",
                "class_name": "Scene02",
            }
        )
        state["current_scene_index"] = 1
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        (project / "plan.json").write_text(
            json.dumps(
                {
                    "title": "Plan",
                    "description": "desc",
                    "target_duration_seconds": 300,
                    "scenes": [
                        {
                            "id": "scene_01",
                            "narration_key": "scene_01",
                            "title": "Scene 1",
                            "description": "desc",
                            "estimated_duration_seconds": 30,
                            "visual_ideas": ["idea"],
                        },
                        {
                            "id": "scene_02",
                            "narration_key": "scene_02",
                            "title": "Scene 2",
                            "description": "desc",
                            "estimated_duration_seconds": 30,
                            "visual_ideas": ["idea"],
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        (project / "narration_script.py").write_text(
            "SCRIPT = {\n"
            "    \"scene_01\": \"Narration text for scene one.\",\n"
            "    \"scene_02\": \"Narration text for scene two.\"\n"
            "}\n",
            encoding="utf-8",
        )
        (project / "scene_02.py").write_text(
            "from manim import *\n\n"
            "class Scene02(VoiceoverScene):\n"
            "    def construct(self):\n"
            "        with self.voiceover(text=SCRIPT[\"scene_02\"]) as tracker:\n"
            "            # SLOT_START:scene_body\n"
            "            title = Text(\"Placeholder\")\n"
            "            self.play(Write(title), run_time=min(1.0, tracker.duration * 0.2))\n"
            "            # SLOT_END:scene_body\n",
            encoding="utf-8",
        )

        calls = {"count": 0}

        def _fake_search(query, limit=10):
            calls["count"] += 1
            return CollectionSearchResult(
                query=query,
                collection_id="collection_test",
                limit=limit,
                chunks=["Should not be used"],
            )

        monkeypatch.setattr(hr_prompts, "search_manim_collection", _fake_search)

        _, user = hr_prompts.compose_prompt(
            phase="build_scenes",
            project_dir=project,
        )

        assert calls["count"] == 0
        assert "Manim CE Reference Documentation" not in user

    def test_narration_prompt_loads(self, tmp_path):
        project = _make_narration_project(tmp_path)
        system, user = hr_prompts.compose_prompt(
            phase="narration",
            project_dir=project,
        )
        assert "voiceover writer" in system
        assert "Narration Test" in user

    def test_plan_prompt_queries_collections_with_user_prompt(self, monkeypatch):
        captured = {}

        def _fake_search(query):
            captured["query"] = query
            return CollectionSearchResult(
                query=query,
                collection_id="collection_test",
                limit=10,
                chunks=["Plan docs chunk"],
            )

        monkeypatch.setattr(hr_prompts, "search_manim_collection", _fake_search)
        _, user = hr_prompts.compose_prompt(
            phase="plan",
            topic="orbital resonance",
            project_dir=Path("."),
        )
        info = hr_prompts.consume_last_retrieval_info()
        assert "Create a video plan for this topic" in captured["query"]
        assert "orbital resonance" in captured["query"]
        assert "Plan docs chunk" not in user
        assert info["phase"] == "plan"
        assert info["hit_count"] == 1

    def test_narration_prompt_queries_collections_with_user_prompt(
        self, monkeypatch, tmp_path
    ):
        project = _make_narration_project(tmp_path)
        captured = {}

        def _fake_search(query):
            captured["query"] = query
            return CollectionSearchResult(
                query=query,
                collection_id="collection_test",
                limit=10,
                chunks=["Narration docs chunk"],
            )

        monkeypatch.setattr(hr_prompts, "search_manim_collection", _fake_search)
        _, user = hr_prompts.compose_prompt(
            phase="narration",
            project_dir=project,
        )
        info = hr_prompts.consume_last_retrieval_info()
        assert "Narration Test" in captured["query"]
        assert "\"scene_01\"" in captured["query"]
        assert "Narration docs chunk" not in user
        assert info["phase"] == "narration"
        assert info["hit_count"] == 1

    def test_scene_qc_prompt_loads(self, tmp_path):
        project = _make_scene_project(tmp_path)
        system, user = hr_prompts.compose_prompt(
            phase="scene_qc",
            project_dir=project,
        )
        assert "Scene QC Phase" in system
        assert "Please review all scene files" in user

    def test_scene_repair_prompt_loads(self, monkeypatch, tmp_path):
        project = _make_scene_project(tmp_path)
        captured = {}

        def _fake_search(query):
            captured["query"] = query
            return CollectionSearchResult(
                query=query,
                collection_id="collection_test",
                limit=10,
                chunks=["repair docs chunk"],
            )

        monkeypatch.setattr(
            hr_prompts,
            "search_manim_collection",
            _fake_search,
        )
        _, user = hr_prompts.compose_prompt(
            phase="scene_repair",
            project_dir=project,
            scene_file=project / "scene_01.py",
            retry_context="boom",
        )
        assert "Current Scene ID" in user
        assert "boom" in user
        assert "Phase: scene_repair" in captured["query"]
        assert "Current scene source:" in captured["query"]
        assert "Full error stacktrace/context:" in captured["query"]
        assert "boom" in captured["query"]


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

class TestCLI:
    def test_missing_project_dir_returns_1(self, monkeypatch, tmp_path):
        missing = tmp_path / "nonexistent"
        monkeypatch.setattr(
            sys, "argv",
            ["prog", "--phase", "plan", "--project-dir", str(missing), "--topic", "test"],
        )
        assert hr_cli.main() == 1

    def test_missing_topic_for_plan_returns_1(self, monkeypatch, tmp_path):
        project = _make_project(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            ["prog", "--phase", "plan", "--project-dir", str(project)],
        )
        assert hr_cli.main() == 1

    def test_missing_scene_file_for_scene_repair_returns_1(self, monkeypatch, tmp_path):
        project = _make_scene_project(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            ["prog", "--phase", "scene_repair", "--project-dir", str(project)],
        )
        assert hr_cli.main() == 1

    def test_dry_run_succeeds(self, monkeypatch, tmp_path):
        project = _make_project(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            [
                "prog",
                "--phase", "plan",
                "--project-dir", str(project),
                "--topic", "quantum computing",
                "--dry-run",
            ],
        )
        assert hr_cli.main() == 0

    def test_dry_run_writes_conversation_log(self, monkeypatch, tmp_path):
        project = _make_project(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            [
                "prog",
                "--phase", "plan",
                "--project-dir", str(project),
                "--topic", "machine learning",
                "--dry-run",
            ],
        )
        hr_cli.main()
        log = project / "log" / "conversation.log"
        assert log.exists()
        content = log.read_text()
        assert "dry_run" in content
        assert "api_mode: responses" in content
        assert "store: True" in content

    def test_api_success_log_includes_previous_and_response_id(self, monkeypatch, tmp_path):
        project = _make_project(tmp_path)
        monkeypatch.setattr(hr_cli, "compose_prompt", lambda **_: ("sys", "user"))
        monkeypatch.setattr(hr_cli, "write_phase_artifacts", lambda **_: True)

        class _Raw:
            id = "resp_current_002"
            content = "{\"ok\": \"yes\"}"
            previous_response_id_used = "resp_prev_001"

        monkeypatch.setattr(
            "harness_responses.client.call_responses_api",
            lambda **_: (_Raw(), _make_valid_plan(9)),
        )
        monkeypatch.setattr(
            sys, "argv",
            [
                "prog",
                "--phase", "plan",
                "--project-dir", str(project),
                "--topic", "test",
            ],
        )
        assert hr_cli.main() == 0
        content = (project / "log" / "conversation.log").read_text(encoding="utf-8")
        assert "store: True" in content
        assert "previous_response_id: resp_prev_001" in content
        assert "response_id: resp_current_002" in content

    def test_build_scenes_includes_uploaded_template_file_reference(
        self, monkeypatch, tmp_path
    ):
        project = _make_scene_project(tmp_path)
        captured = {}

        def _fake_compose_prompt(**kwargs):
            captured["template_file_reference"] = kwargs.get("template_file_reference", "")
            return ("sys", "user")

        class _Raw:
            id = "resp_scene_1"
            content = "{\"ok\": \"yes\"}"
            previous_response_id_used = None

        monkeypatch.setattr(hr_cli, "compose_prompt", _fake_compose_prompt)
        monkeypatch.setattr(hr_cli, "write_phase_artifacts", lambda **_: True)
        monkeypatch.setattr(
            "harness_responses.client.ensure_build_scenes_template_file",
            lambda **_: {
                "template_file_id": "file_template_001",
                "template_hash": "hash",
                "uploaded": False,
            },
        )
        monkeypatch.setattr(
            "harness_responses.client.call_responses_api",
            lambda **_: (_Raw(), BuildScenesResponse(scene_body="title = Text('x')")),
        )
        monkeypatch.setattr(
            sys, "argv",
            [
                "prog",
                "--phase", "build_scenes",
                "--project-dir", str(project),
            ],
        )
        assert hr_cli.main() == 0
        ref = captured.get("template_file_reference", "")
        assert "file_template_001" in ref

    def test_retry_context_clears_response_pointer_before_api_call(
        self, monkeypatch, tmp_path
    ):
        project = _make_project(tmp_path)
        cleared = {"called": False}

        def _fake_clear_response_pointer(**_kwargs):
            cleared["called"] = True

        monkeypatch.setattr(hr_cli, "compose_prompt", lambda **_: ("sys", "user"))
        monkeypatch.setattr(hr_cli, "write_phase_artifacts", lambda **_: True)
        monkeypatch.setattr(
            "harness_responses.client.clear_response_pointer",
            _fake_clear_response_pointer,
        )

        class _Raw:
            id = "resp_retry_1"
            content = "{\"ok\": \"yes\"}"
            previous_response_id_used = None

        monkeypatch.setattr(
            "harness_responses.client.call_responses_api",
            lambda **_: (_Raw(), _make_valid_plan(9)),
        )
        monkeypatch.setattr(
            sys, "argv",
            [
                "prog",
                "--phase", "plan",
                "--project-dir", str(project),
                "--topic", "test",
                "--retry-context", "Traceback ...",
            ],
        )
        assert hr_cli.main() == 0
        assert cleared["called"] is True

    def test_semantic_validation_failure_returns_2(self, monkeypatch, tmp_path):
        project = _make_project(tmp_path)

        def _fake_prompt(**_kwargs):
            return ("sys", "user")

        def _fake_write(*args, **kwargs):
            raise SemanticValidationError("Too few scenes")

        monkeypatch.setattr(hr_cli, "compose_prompt", _fake_prompt)
        monkeypatch.setattr(
            "harness_responses.client.call_responses_api",
            lambda **kw: (_MockResponse(), _make_valid_plan(9)),
        )
        monkeypatch.setattr(hr_cli, "write_phase_artifacts", _fake_write)
        monkeypatch.setattr(
            sys, "argv",
            [
                "prog",
                "--phase", "plan",
                "--project-dir", str(project),
                "--topic", "test",
            ],
        )
        assert hr_cli.main() == 2

    def test_api_key_missing_returns_2(self, monkeypatch, tmp_path):
        project = _make_project(tmp_path)
        monkeypatch.setattr(hr_cli, "compose_prompt", lambda **_: ("sys", "user"))
        # Patch at the source module so the lazy import picks it up
        monkeypatch.setattr(
            "harness_responses.client.call_responses_api",
            lambda **_: (_ for _ in ()).throw(EnvironmentError("XAI_API_KEY not set")),
        )
        monkeypatch.setattr(
            sys, "argv",
            [
                "prog",
                "--phase", "plan",
                "--project-dir", str(project),
                "--topic", "test",
            ],
        )
        assert hr_cli.main() == 2

    def test_module_entrypoint(self, monkeypatch):
        called = {"ok": False}

        def fake_main():
            called["ok"] = True
            return 0

        monkeypatch.setattr("harness_responses.cli.main", fake_main)
        with pytest.raises(SystemExit) as ex:
            runpy.run_module("harness_responses.__main__", run_name="__main__")
        assert ex.value.code == 0
        assert called["ok"] is True


class _MockResponse:
    """Minimal mock for xai_sdk Response."""
    id = "mock_response_id_123"

    def __init__(self, content: str = "mock content"):
        self.content = content


# ---------------------------------------------------------------------------
# Legacy harness isolation test
# ---------------------------------------------------------------------------

class TestLegacyHarnessIsolation:
    def test_no_import_from_legacy_harness(self):
        """harness_responses modules must not import from harness/."""
        import ast

        hr_root = Path(__file__).parent.parent.parent / "harness_responses"
        for py_file in hr_root.rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        assert not node.module.startswith("harness."), (
                            f"{py_file} imports from legacy harness/: {node.module}"
                        )
