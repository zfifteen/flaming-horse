"""
Tests for harness_responses plan phase.

Covers:
  - Pydantic schema validation (pass/fail)
  - Semantic validation (scene count, duration bounds)
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
import harness_responses.parser as hr_parser
import harness_responses.prompts as hr_prompts
from harness_responses.schemas.plan import PlanResponse, SceneItem
from harness_responses.parser import SemanticValidationError


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


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------

class TestPlanSchema:
    def test_valid_plan_parses(self):
        plan = _make_valid_plan()
        assert plan.title == "Test Video"
        assert len(plan.scenes) == 9

    def test_schema_requires_title(self):
        with pytest.raises(ValidationError):
            PlanResponse(
                title="",
                description="desc",
                target_duration_seconds=300,
                scenes=[_make_valid_scene()],
            )

    def test_scene_requires_visual_ideas(self):
        with pytest.raises(ValidationError):
            SceneItem(
                title="Scene",
                description="desc",
                estimated_duration_seconds=30,
                visual_ideas=[],
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

    def test_too_few_scenes_fails(self, tmp_path):
        project = _make_project(tmp_path)
        plan = _make_valid_plan(7)  # below minimum of 8
        with pytest.raises(SemanticValidationError, match="scenes must have"):
            hr_parser.validate_and_write_plan(plan, project)

    def test_too_many_scenes_fails(self, tmp_path):
        project = _make_project(tmp_path)
        plan = _make_valid_plan(13)  # above maximum of 12
        with pytest.raises(SemanticValidationError, match="scenes must have"):
            hr_parser.validate_and_write_plan(plan, project)

    def test_invalid_total_duration_fails(self, tmp_path):
        project = _make_project(tmp_path)
        plan = PlanResponse(
            title="Test",
            description="desc",
            target_duration_seconds=100,  # below 240
            scenes=[_make_valid_scene(i) for i in range(9)],
        )
        with pytest.raises(SemanticValidationError, match="target_duration_seconds"):
            hr_parser.validate_and_write_plan(plan, project)

    def test_invalid_scene_duration_fails(self, tmp_path):
        project = _make_project(tmp_path)
        scenes = [_make_valid_scene(i) for i in range(9)]
        scenes[3] = SceneItem(
            title="Bad scene",
            description="desc",
            estimated_duration_seconds=10,  # below 20
            visual_ideas=["idea"],
        )
        plan = PlanResponse(
            title="Test",
            description="desc",
            target_duration_seconds=300,
            scenes=scenes,
        )
        with pytest.raises(SemanticValidationError, match="estimated_duration_seconds"):
            hr_parser.validate_and_write_plan(plan, project)

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
        plan = _make_valid_plan(7)  # will fail
        with pytest.raises(SemanticValidationError):
            hr_parser.validate_and_write_plan(plan, project, raw_response=None)
        diag = project / "log" / "responses_last_response.json"
        assert diag.exists()
        data = json.loads(diag.read_text())
        assert "validation_error" in data

    def test_write_phase_artifacts_plan(self, tmp_path):
        project = _make_project(tmp_path)
        plan = _make_valid_plan(9)
        assert hr_parser.write_phase_artifacts("plan", plan, project) is True

    def test_write_phase_artifacts_unimplemented_phase_raises(self, tmp_path):
        project = _make_project(tmp_path)
        with pytest.raises(NotImplementedError):
            hr_parser.write_phase_artifacts("narration", None, project)


# ---------------------------------------------------------------------------
# Prompt composition tests
# ---------------------------------------------------------------------------

class TestPromptComposition:
    def test_plan_prompts_load(self):
        system, user = hr_prompts.compose_prompt(phase="plan", topic="black holes")
        assert "Manim" in system
        assert "black holes" in user

    def test_unknown_phase_raises(self):
        with pytest.raises(ValueError, match="not implemented"):
            hr_prompts.compose_prompt(phase="narration", topic="test")

    def test_retry_context_appended(self):
        _, user = hr_prompts.compose_prompt(
            phase="plan", topic="test", retry_context="previous error details"
        )
        assert "previous error details" in user

    def test_no_retry_context_clean(self):
        _, user = hr_prompts.compose_prompt(phase="plan", topic="test", retry_context="")
        assert "Retry context" not in user


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
        assert "store: False" in content

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
    content = "mock content"


# ---------------------------------------------------------------------------
# Legacy harness isolation test
# ---------------------------------------------------------------------------

class TestLegacyHarnessIsolation:
    def test_no_import_from_legacy_harness(self):
        """harness_responses modules must not import from harness/."""
        import ast
        import os

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
