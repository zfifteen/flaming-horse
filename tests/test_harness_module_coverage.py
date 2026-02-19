import json
import runpy
import sys
from pathlib import Path

import pytest
import requests

import harness.cli as cli
import harness.client as client
import harness.parser as parser
import harness.prompts as prompts
from scripts.scaffold_scene import TEMPLATE


class _Resp:
    def __init__(self, status_code=200, data=None, text="ok", raise_http=False):
        self.status_code = status_code
        self._data = data or {"choices": [{"message": {"content": "ok"}}]}
        self.text = text
        self._raise_http = raise_http

    def json(self):
        return self._data

    def raise_for_status(self):
        if self._raise_http:
            err = requests.exceptions.HTTPError(self.text)
            err.response = self
            raise err


def _mk_state_file(project_dir: Path, state: dict | None = None):
    state = state or {"phase": "plan", "scenes": [], "current_scene_index": 0}
    (project_dir / "project_state.json").write_text(json.dumps(state), encoding="utf-8")


def test_main_module_entrypoint(monkeypatch):
    called = {"ok": False}

    def fake_main():
        called["ok"] = True
        return 0

    monkeypatch.setattr("harness.cli.main", fake_main)
    with pytest.raises(SystemExit) as ex:
        runpy.run_module("harness.__main__", run_name="__main__")
    assert ex.value.code == 0
    assert called["ok"] is True


def test_cli_validations_and_dry_run(monkeypatch, tmp_path, capsys):
    missing = tmp_path / "missing"
    monkeypatch.setattr(
        sys, "argv", ["prog", "--phase", "plan", "--project-dir", str(missing)]
    )
    assert cli.main() == 1

    project = tmp_path / "project"
    project.mkdir()
    _mk_state_file(project)

    monkeypatch.setattr(
        sys, "argv", ["prog", "--phase", "plan", "--project-dir", str(project)]
    )
    assert cli.main() == 1

    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "--phase", "scene_repair", "--project-dir", str(project)],
    )
    assert cli.main() == 1

    monkeypatch.setattr(cli, "compose_prompt", lambda **_: ("sys", "user"))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--phase",
            "plan",
            "--project-dir",
            str(project),
            "--topic",
            "t",
            "--dry-run",
        ],
    )
    assert cli.main() == 0
    out = capsys.readouterr().out
    assert "DRY RUN MODE" in out


def test_cli_happy_path_and_fail_paths(monkeypatch, tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    _mk_state_file(project)

    monkeypatch.setattr(cli, "compose_prompt", lambda **_: ("sys", "user"))
    monkeypatch.setattr(cli, "call_xai_api", lambda **_: "resp")
    monkeypatch.setattr(cli, "parse_and_write_artifacts", lambda **_: True)
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "--phase", "plan", "--project-dir", str(project), "--topic", "t"],
    )
    monkeypatch.setenv("AGENT_TEMPERATURE", "not-a-float")
    assert cli.main() == 0

    monkeypatch.setattr(cli, "parse_and_write_artifacts", lambda **_: False)
    assert cli.main() == 2
    assert (project / "log" / "debug_response_plan.txt").exists()

    monkeypatch.setattr(
        cli,
        "parse_and_write_artifacts",
        lambda **_: (_ for _ in ()).throw(parser.SchemaValidationError("bad schema")),
    )
    assert cli.main() == 3

    monkeypatch.setattr(cli, "load_project_state", lambda _: (_ for _ in ()).throw(FileNotFoundError("x")))
    assert cli.main() == 1

    monkeypatch.setattr(cli, "load_project_state", lambda _: {"phase": "plan", "scenes": [], "current_scene_index": 0})
    monkeypatch.setattr(cli, "compose_prompt", lambda **_: (_ for _ in ()).throw(RuntimeError("boom")))
    assert cli.main() == 1


def test_client_init_and_aliases(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("XAI_API_KEY", "k")
    c = client.LLMClient()
    assert c.provider == "XAI"
    assert client.XAIClient is client.LLMClient
    assert client.estimate_tokens("abcd") == 1

    monkeypatch.setenv("LLM_PROVIDER", "MINIMAX")
    monkeypatch.setenv("MINIMAX_API_KEY", "m")
    c2 = client.LLMClient(model="xai/custom")
    assert c2.model == "custom"

    monkeypatch.setenv("LLM_PROVIDER", "BAD")
    with pytest.raises(ValueError):
        client.LLMClient(api_key="x")

    monkeypatch.setenv("LLM_PROVIDER", "MINIMAX")
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    with pytest.raises(ValueError):
        client.LLMClient()


def test_client_request_branches(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "XAI")
    monkeypatch.setenv("XAI_API_KEY", "k")
    c = client.LLMClient()

    calls = {"n": 0}

    def post_ok(*args, **kwargs):
        calls["n"] += 1
        return _Resp(200, {"choices": [{"message": {"content": "done"}}]})

    monkeypatch.setattr(client.requests, "post", post_ok)
    assert c.chat_completion("s", "u") == "done"

    def post_429_then_ok(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 2:
            return _Resp(429, text="rate")
        return _Resp(200, {"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(client.requests, "post", post_429_then_ok)
    monkeypatch.setattr(client.time, "sleep", lambda *_: None)
    assert c.chat_completion("s", "u") == "ok"

    def post_500(*args, **kwargs):
        return _Resp(500, text="server", raise_http=True)

    monkeypatch.setattr(client.requests, "post", post_500)
    with pytest.raises(requests.exceptions.HTTPError):
        c.chat_completion("s", "u")

    def post_400(*args, **kwargs):
        return _Resp(400, text="bad", raise_http=True)

    monkeypatch.setattr(client.requests, "post", post_400)
    with pytest.raises(requests.exceptions.HTTPError):
        c.chat_completion("s", "u")

    class _REx(requests.exceptions.RequestException):
        pass

    def post_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(client.requests, "post", post_timeout)
    with pytest.raises(requests.exceptions.Timeout):
        c.chat_completion("s", "u")

    def post_reqerr(*args, **kwargs):
        raise _REx("x")

    monkeypatch.setattr(client.requests, "post", post_reqerr)
    with pytest.raises(_REx):
        c.chat_completion("s", "u")

    def post_bad_shape(*args, **kwargs):
        return _Resp(200, {"choices": [{}]})

    monkeypatch.setattr(client.requests, "post", post_bad_shape)
    with pytest.raises(ValueError):
        c.chat_completion("s", "u")


def test_call_llm_api_alias(monkeypatch):
    monkeypatch.setattr(client, "LLMClient", lambda: type("C", (), {"chat_completion": lambda *args, **kwargs: "ok"})())
    assert client.call_llm_api("s", "u") == "ok"
    assert client.call_xai_api("s", "u") == "ok"


def test_prompts_core_and_compose(tmp_path):
    with pytest.raises(FileNotFoundError):
        prompts.read_file(tmp_path / "missing.txt")

    assert prompts.render_template("hi {{a}}", {"a": "x"}) == "hi x"
    assert prompts.render_template("{{a}} {{b}}", {"a": 1}) == "1 "
    assert prompts.render_template("{{{{X}}}}", {}) == "{{X}}"

    with pytest.raises(ValueError):
        prompts.load_prompt_template("bad", "x.md", {})

    assert prompts.scene_id_to_class_name("scene_01_intro") == "Scene01Intro"

    assert prompts.extract_scene_narration("not python", "k") is None
    assert prompts.extract_scene_narration("SCRIPT = []", "k") is None
    assert prompts.extract_scene_narration("SCRIPT = {'k': '  v  '}", "k") == "v"

    project = tmp_path / "p"
    project.mkdir()
    plan = {
        "title": "T",
        "scenes": [{"id": "scene_01_intro", "title": "Intro", "narration_key": "scene_01_intro"}],
    }
    (project / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
    (project / "narration_script.py").write_text("SCRIPT = {'scene_01_intro': 'Narr'}", encoding="utf-8")
    (project / "scene_01_intro.py").write_text("print('x')", encoding="utf-8")

    state = {
        "plan_file": "plan.json",
        "narration_file": "narration_script.py",
        "scenes": [{"id": "scene_01_intro", "title": "Intro", "file": "scene_01_intro.py", "narration_key": "scene_01_intro"}],
        "current_scene_index": 0,
    }

    for phase in ("plan", "review", "narration", "build_scenes", "scene_qc"):
        s, u = prompts.compose_prompt(phase=phase, state=state, topic="topic", project_dir=project)
        assert isinstance(s, str) and isinstance(u, str)

    s, u = prompts.compose_prompt(
        phase="scene_repair",
        state=state,
        project_dir=project,
        scene_file=project / "scene_01_intro.py",
        retry_context="err",
    )
    assert "err" in u

    # scene_repair missing scene_file
    with pytest.raises(ValueError):
        prompts.compose_prompt(phase="scene_repair", state=state, project_dir=project)
    with pytest.raises(ValueError):
        prompts.compose_prompt(phase="unknown", state=state, project_dir=project)
    with pytest.raises(ValueError):
        prompts.compose_prompt(phase="plan", state=state)

    # missing narration key for build_scenes
    (project / "narration_script.py").write_text("SCRIPT = {}", encoding="utf-8")
    with pytest.raises(ValueError):
        prompts.compose_prompt(phase="build_scenes", state=state, project_dir=project)


def test_parser_helpers_and_phase_parsers(tmp_path):
    assert parser.strip_harness_preamble("🤖 Harness using:\nProvider: X\nBase URL: b\nModel: m\n```python\nx=1\n```").startswith("```python")
    assert parser.strip_harness_preamble("plain") == "plain"

    assert parser.extract_json_block('wrapper {"a":1}') is not None
    assert parser.extract_json_block('{"a":1}') is not None
    assert parser.extract_json_block("bad") is None

    assert parser.extract_single_python_code("```python\nx=1\n```") == "x=1"
    assert parser.extract_single_python_code("SCRIPT = {\n  'a': 'b'\n}\nnoise") is not None
    assert parser.extract_single_python_code("import x\nx=1") is not None
    assert parser.extract_single_python_code("no code here") is None

    assert parser.sanitize_code("<scene_body>\n```python\nx=1\n```\n</scene_body>").strip() == "x=1"
    assert parser.verify_python_syntax("x=1")
    assert not parser.verify_python_syntax("x=")
    assert not parser.validate_scene_body_syntax("x=")
    assert parser.validate_scene_body_syntax("x=1")

    assert parser.parse_plan_response('{"title":"t","scenes":[{"id":"scene_01_intro","title":"Intro","narration_key":"scene_01_intro"}]}')["title"] == "t"
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_plan_response('{"plan":{"title":"t","scenes":[]}}')
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_plan_response("bad")

    narr = parser.parse_narration_response('{"script":{"k":"v"}}')
    assert narr is not None and "SCRIPT = {" in narr
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_narration_response('["x"]')
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_narration_response('{"k":1}')

    assert parser.extract_scene_body_xml("<scene_body>x=1</scene_body>") == "x=1"
    assert parser.extract_scene_body_xml("x=1") is None
    full = "with self.voiceover(text=SCRIPT['k']) as tracker:\n            x=1\n            y=2\n"
    assert parser.extract_scene_body_from_full_file(full).startswith("x=1")

    assert parser.parse_build_scenes_response('{"scene_body":"self.play(Write(x))"}') == "self.play(Write(x))"
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_build_scenes_response('{"scene_body":"x=1"}')
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_build_scenes_response("x=1")
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_build_scenes_response('{"scene_body":"from manim import *\\nself.play(Write(x))"}')

    scene_files, report = parser.parse_scene_qc_response('{"report_markdown":"# Scene QC Report\\nok"}')
    assert len(scene_files) == 0
    assert report is not None

    assert parser.parse_scene_repair_response('{"scene_body":"self.play(Write(x))"}') == "self.play(Write(x))"
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_scene_repair_response('{"scene_body":"x=1"}')
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_scene_repair_response("```python\nx=1\n```")
    assert parser.class_name_to_scene_filename("Scene01Intro") == "scene_01_intro.py"
    assert parser.class_name_to_scene_filename("Scene10FarewellIllusion") == "scene_10_farewell_illusion.py"

    # inject body
    scaffold = tmp_path / "s.py"
    scaffold.write_text(TEMPLATE.format(class_name="X", narration_key="k"), encoding="utf-8")
    injected = parser.inject_body_into_scaffold(scaffold, "x=1")
    assert "x=1" in injected
    with pytest.raises(ValueError):
        parser.inject_body_into_scaffold(scaffold, "# only comment")
    no_marker = tmp_path / "no_marker.py"
    no_marker.write_text("print('no slots')\n", encoding="utf-8")
    with pytest.raises(ValueError):
        parser.inject_body_into_scaffold(no_marker, "x=1")


def test_parse_and_write_artifacts_branches(tmp_path, monkeypatch):
    project = tmp_path / "p"
    project.mkdir()
    scene = project / "scene_01.py"
    scene.write_text(TEMPLATE.format(class_name="Scene01", narration_key="scene_01"), encoding="utf-8")
    state = {
        "scenes": [{"id": "scene_01", "file": "scene_01.py"}],
        "current_scene_index": 0,
    }

    assert parser.parse_and_write_artifacts(
        "plan",
        '{"title":"t","scenes":[{"id":"scene_01_intro","title":"Intro","narration_key":"scene_01_intro"}]}',
        project,
        state,
    )
    assert parser.parse_and_write_artifacts("narration", '{"script":{"k":"v"}}', project, state)
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_and_write_artifacts("narration", "bad", project, state)
    assert parser.parse_and_write_artifacts("build_scenes", '{"scene_body":"self.play(Write(x))"}', project, state)
    assert parser.parse_and_write_artifacts("scene_repair", '{"scene_body":"self.play(Write(x))"}', project, {**state, "scene_file": str(scene)})

    qc = '{"report_markdown":"# Scene QC Report\\nok"}'
    assert parser.parse_and_write_artifacts("scene_qc", qc, project, state)
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_and_write_artifacts("scene_qc", "no artifacts", project, state)

    with pytest.raises(parser.SchemaValidationError):
        parser.parse_and_write_artifacts("build_scenes", "bad", project, state)
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_and_write_artifacts("scene_repair", "bad", project, state)
    assert not parser.parse_and_write_artifacts("unknown", "x", project, state)

    bad_state = {"scenes": [], "current_scene_index": 1}
    assert not parser.parse_and_write_artifacts("build_scenes", '{"scene_body":"self.play(Write(x))"}', project, bad_state)

    # force injection failure
    monkeypatch.setattr(parser, "inject_body_into_scaffold", lambda *a, **k: (_ for _ in ()).throw(ValueError("boom")))
    assert not parser.parse_and_write_artifacts("scene_repair", '{"scene_body":"self.play(Write(x))"}', project, {**state, "scene_file": str(scene)})


def test_cli_additional_branches(monkeypatch, tmp_path):
    missing_project = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        cli.load_project_state(missing_project)

    project = tmp_path / "project"
    project.mkdir()
    _mk_state_file(project)
    scene_file = project / "scene_01.py"
    scene_file.write_text("print('x')\n", encoding="utf-8")

    monkeypatch.setattr(cli, "compose_prompt", lambda **_: ("sys", "user"))
    monkeypatch.setattr(cli, "call_xai_api", lambda **_: "resp")
    monkeypatch.setattr(cli, "parse_and_write_artifacts", lambda **_: False)

    orig_write_text = Path.write_text

    def fail_debug_write(self, data, *args, **kwargs):
        if self.name.startswith("debug_response_"):
            raise OSError("no write")
        return orig_write_text(self, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_debug_write)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--phase",
            "scene_repair",
            "--project-dir",
            str(project),
            "--scene-file",
            str(scene_file),
        ],
    )
    assert cli.main() == 2


def test_cli_main_guard_line(monkeypatch, tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    _mk_state_file(project)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "harness.cli",
            "--phase",
            "plan",
            "--project-dir",
            str(project),
            "--topic",
            "t",
            "--dry-run",
        ],
    )
    with pytest.raises(SystemExit) as ex:
        runpy.run_module("harness.cli", run_name="__main__")
    assert ex.value.code == 0


def test_client_additional_branches(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "XAI")
    monkeypatch.setenv("XAI_API_KEY", "env-key")
    c = client.LLMClient(api_key="direct-key", base_url="https://example.test", model="minimax/m")
    assert c.api_key == "direct-key"
    assert c.base_url == "https://example.test"
    assert c.model == "m"

    monkeypatch.setenv("LLM_PROVIDER", "XAI")
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        client.LLMClient()

    monkeypatch.setenv("LLM_PROVIDER", "XAI")
    monkeypatch.setenv("XAI_API_KEY", "k")
    c2 = client.LLMClient()
    c2.max_retries = 1
    c2.retry_delay = 0
    monkeypatch.setattr(client.time, "sleep", lambda *_: None)
    monkeypatch.setattr(client.requests, "post", lambda *a, **k: _Resp(429, text="rate"))
    with pytest.raises(Exception, match="Failed to get response"):
        c2.chat_completion("s", "u")


def test_prompts_additional_branches(tmp_path):
    project = tmp_path / "p"
    project.mkdir()
    (project / "plan.json").write_text(json.dumps({"title": "T", "scenes": []}), encoding="utf-8")
    (project / "narration_script.py").write_text("SCRIPT = {'scene_04': 'Narr'}", encoding="utf-8")

    assert prompts.resolve_project_file(project, "", "default.txt") == project / "default.txt"
    assert prompts.extract_scene_narration("def broken(", "k") is None
    assert prompts.extract_scene_narration("A = {'k': 1}", "k") is None
    assert prompts.extract_scene_narration("SCRIPT = unknown_name", "k") is None

    state = {"current_scene_index": 3, "scenes": []}
    sys_prompt, user_prompt = prompts.compose_build_scenes_prompt(state, project, retry_context="boom")
    assert isinstance(sys_prompt, str)
    assert "RETRY CONTEXT" in user_prompt


def test_parser_additional_helpers_and_parsers(tmp_path, monkeypatch):
    assert parser.strip_harness_preamble("\n\n") == "\n\n"
    stripped = parser.strip_harness_preamble("\n🤖 Harness using:\nProvider: X\n\nModel: M\n\n```python\nx=1\n```")
    assert stripped.startswith("```python")

    assert parser.extract_json_block('```json\n{"a": 1} trailing\n```') == '{"a": 1}'
    assert parser.extract_json_block("noise {\"a\":1} tail") == '{"a": 1}'
    assert parser.extract_json_block("```json\nnot-json\n```") is None
    assert parser.extract_json_block("bad {a:1}") is None
    assert parser.extract_json_block("{{") is None
    assert parser.extract_json_block('x {{"a":1}}') == '{"a": 1}'
    assert parser.extract_json_block('  "json-string"  ') is None

    assert parser.extract_scene_body_from_full_file("no voiceover here") is None
    full = "with self.voiceover(text=SCRIPT['k']) as tracker:\n        x=1\n  y=2\n"
    body = parser.extract_scene_body_from_full_file(full)
    assert body is not None and "x=1" in body and "y=2" in body
    assert parser.extract_single_python_code("SCRIPT = {\n  'a': 'b'\n") == "SCRIPT = {\n  'a': 'b'"

    with pytest.raises(parser.SchemaValidationError):
        parser.parse_plan_response('{"title":"t","scenes":{"bad":1}}')
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_plan_response('{"x": 1}')
    valid = parser.parse_plan_response('{"title":"t","scenes":[{"id":"scene_01_intro","title":"Intro","narration_key":"scene_01_intro"}]}')
    assert valid is not None and valid["scenes"][0]["narration_key"] == "scene_01_intro"
    monkeypatch.setattr(parser, "extract_json_block", lambda _: "{'title': 't', 'scenes': []}")
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_plan_response("ignored")
    monkeypatch.setattr(parser, "extract_json_block", lambda _: "{")
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_plan_response("ignored")
    monkeypatch.setattr(parser, "extract_json_block", lambda _: None)

    monkeypatch.setattr(parser, "extract_json_block", lambda _: "{")
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_narration_response("x")
    monkeypatch.setattr(parser, "extract_json_block", lambda _: None)

    with pytest.raises(parser.SchemaValidationError):
        parser.parse_build_scenes_response("```python\n<scene_body>\n</scene_body>\n```")
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_build_scenes_response("```python\n<abc></abc>\n```")
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_build_scenes_response('{"scene_body":"x="}')
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_build_scenes_response('{"scene_body":"def f():\\n    pass"}')

    with pytest.raises(parser.SchemaValidationError):
        parser.parse_scene_repair_response('{"scene_body":"x="}')
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_scene_repair_response("import os\nx=")
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_scene_repair_response("import os\nx=1")
    with pytest.raises(parser.SchemaValidationError):
        parser.parse_scene_repair_response('{"scene_body":"# c\\nimport os\\nself.play(Write(x))"}')

    marker_missing_end = tmp_path / "missing_end.py"
    marker_missing_end.write_text("# SLOT_START:scene_body\n", encoding="utf-8")
    with pytest.raises(ValueError):
        parser.inject_body_into_scaffold(marker_missing_end, "x=1")

    scaffold = tmp_path / "good.py"
    scaffold.write_text(TEMPLATE.format(class_name="X", narration_key="k"), encoding="utf-8")
    injected = parser.inject_body_into_scaffold(scaffold, "x=1\n\n    y=2")
    assert "            y=2" in injected
    assert parser.validate_scene_body_syntax("choice([1,2])")


def test_parse_and_write_artifacts_additional_branches(tmp_path, monkeypatch):
    project = tmp_path / "p"
    project.mkdir()
    scene_file = project / "scene_01.py"
    scene_file.write_text(TEMPLATE.format(class_name="Scene01", narration_key="scene_01"), encoding="utf-8")
    state = {"scenes": [{"id": "scene_01", "file": "scene_01.py"}], "current_scene_index": 0}

    with pytest.raises(parser.SchemaValidationError):
        parser.parse_and_write_artifacts("plan", "bad", project, state)

    monkeypatch.setattr(parser, "parse_build_scenes_response", lambda *_: "x=1")
    monkeypatch.setattr(parser, "validate_scene_body_syntax", lambda *_: False)
    assert not parser.parse_and_write_artifacts("build_scenes", "ignored", project, state)

    monkeypatch.setattr(parser, "validate_scene_body_syntax", lambda *_: True)
    missing_state = {"scenes": [{"id": "scene_01", "file": "missing.py"}], "current_scene_index": 0}
    assert not parser.parse_and_write_artifacts("build_scenes", "ignored", project, missing_state)

    monkeypatch.setattr(parser, "inject_body_into_scaffold", lambda *a, **k: (_ for _ in ()).throw(ValueError("bad inject")))
    assert not parser.parse_and_write_artifacts("build_scenes", "ignored", project, state)

    qc_with_class = '{"report_markdown":"# Scene QC Report\\nok"}'
    assert parser.parse_and_write_artifacts("scene_qc", qc_with_class, project, state)

    canonical_state = {
        "scenes": [
            {
                "id": "scene_01_welcome_to_reality",
                "class_name": "Scene01WelcomeToReality",
                "file": "scene_01_welcome_to_reality.py",
            }
        ],
        "current_scene_index": 0,
    }
    qc_canonical = '{"report_markdown":"# Scene QC Report\\nok"}'
    assert parser.parse_and_write_artifacts("scene_qc", qc_canonical, project, canonical_state)

    qc_without_class = '{"report_markdown":"# Scene QC Report\\nok"}'
    assert parser.parse_and_write_artifacts("scene_qc", qc_without_class, project, state)

    monkeypatch.setattr(parser, "parse_scene_repair_response", lambda *_: "x=1")
    monkeypatch.setattr(parser, "validate_scene_body_syntax", lambda *_: False)
    assert not parser.parse_and_write_artifacts("scene_repair", "ignored", project, state)

    monkeypatch.setattr(parser, "validate_scene_body_syntax", lambda *_: True)
    no_scene_state = {"scenes": [], "current_scene_index": 0}
    assert not parser.parse_and_write_artifacts("scene_repair", "ignored", project, no_scene_state)

    monkeypatch.setattr(parser, "inject_body_into_scaffold", lambda scaffold, body: "print('ok')\n")
    relative_state = {"scenes": [{"file": "scene_01.py"}], "current_scene_index": 0}
    assert parser.parse_and_write_artifacts("scene_repair", "ignored", project, relative_state)

    monkeypatch.setattr(parser, "parse_plan_response", lambda *_: (_ for _ in ()).throw(RuntimeError("boom")))
    assert not parser.parse_and_write_artifacts("plan", "{}", project, state)
