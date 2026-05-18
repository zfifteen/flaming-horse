#!/usr/bin/env python3
"""Tests for scripts/tts_backend_config.py."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from tts_backend_config import (  # noqa: E402
    DEFAULT_MLX_MODEL_ID,
    build_voice_clone_config,
    main,
    selected_model_id,
    selected_output_dir,
    selected_tts_backend,
    selected_worker_python_raw,
    write_voice_clone_config,
)


class TestTtsBackendConfig(unittest.TestCase):
    def test_mlx_backend_uses_mlx_python_not_qwen_python(self):
        cfg = {
            "backend": "mlx",
            "qwen_python": "/missing/qwen/python",
            "worker_python": "/project/mlx/python",
            "model_id": DEFAULT_MLX_MODEL_ID,
        }
        env = {
            "FLAMING_HORSE_TTS_BACKEND": "mlx",
            "FLAMING_HORSE_MLX_PYTHON": "/repo/.venv/bin/python",
        }
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(selected_tts_backend(), "mlx")
            self.assertEqual(
                selected_worker_python_raw(cfg, "mlx"),
                "/repo/.venv/bin/python",
            )
            self.assertEqual(selected_model_id(cfg, "mlx"), DEFAULT_MLX_MODEL_ID)

    def test_mlx_backend_ignores_generic_python(self):
        cfg = {
            "backend": "mlx",
            "worker_python": "/project/mlx/python",
            "model_id": DEFAULT_MLX_MODEL_ID,
        }
        env = {"PYTHON": "/wrong/orchestrator/python"}
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(
                selected_worker_python_raw(cfg, "mlx"),
                "/project/mlx/python",
            )

    def test_project_config_selects_backend_when_env_is_unset(self):
        cfg = {
            "backend": "mlx",
            "worker_python": "/repo/.venv/bin/python",
            "model_id": DEFAULT_MLX_MODEL_ID,
        }
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(selected_tts_backend(cfg), "mlx")
            self.assertEqual(
                selected_worker_python_raw(cfg, "mlx"),
                "/repo/.venv/bin/python",
            )

    def test_missing_mlx_worker_python_fails(self):
        cfg = {"backend": "mlx", "model_id": DEFAULT_MLX_MODEL_ID}
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Missing MLX worker Python"):
                selected_worker_python_raw(cfg, "mlx")

    def test_backend_env_config_mismatch_fails(self):
        cfg = {"backend": "mlx", "worker_python": "/project/mlx/python"}
        with patch.dict(
            os.environ, {"FLAMING_HORSE_TTS_BACKEND": "qwen"}, clear=True
        ):
            with self.assertRaisesRegex(ValueError, "TTS backend mismatch"):
                selected_tts_backend(cfg)

    def test_qwen_backend_uses_qwen_python(self):
        cfg = {
            "backend": "qwen",
            "qwen_python": "/project/qwen/python",
            "model_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        }
        env = {
            "FLAMING_HORSE_TTS_BACKEND": "qwen",
            "FLAMING_HORSE_QWEN_PYTHON": "/env/qwen/python",
        }
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(selected_tts_backend(), "qwen")
            self.assertEqual(
                selected_worker_python_raw(cfg, "qwen"),
                "/env/qwen/python",
            )
            self.assertEqual(
                selected_model_id(cfg, "qwen"),
                "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            )

    def test_qwen_backend_accepts_worker_python_fallback(self):
        cfg = {
            "backend": "qwen",
            "worker_python": "/project/neutral/python",
            "model_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        }
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                selected_worker_python_raw(cfg, "qwen"),
                "/project/neutral/python",
            )

    def test_build_voice_clone_config_uses_shared_precedence(self):
        env = {
            "FLAMING_HORSE_TTS_BACKEND": "mlx",
            "FLAMING_HORSE_MLX_PYTHON": "/env/mlx/python",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = build_voice_clone_config({})
            self.assertEqual(cfg["backend"], "mlx")
            self.assertEqual(cfg["worker_python"], "/env/mlx/python")
            self.assertNotIn("qwen_python", cfg)
            self.assertEqual(cfg["output_dir"], "media/voiceovers/qwen")

    def test_mlx_config_preserves_explicit_legacy_qwen_python_only(self):
        env = {
            "FLAMING_HORSE_TTS_BACKEND": "mlx",
            "FLAMING_HORSE_MLX_PYTHON": "/env/mlx/python",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = build_voice_clone_config({"qwen_python": "/legacy/qwen/python"})
            self.assertEqual(cfg["qwen_python"], "/legacy/qwen/python")

    def test_output_dir_env_override_is_written_to_new_config(self):
        env = {
            "FLAMING_HORSE_TTS_BACKEND": "mlx",
            "FLAMING_HORSE_MLX_PYTHON": "/env/mlx/python",
            "FLAMING_HORSE_TTS_OUTPUT_DIR": "media/voiceovers/neutral",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = build_voice_clone_config({})
            self.assertEqual(cfg["output_dir"], "media/voiceovers/neutral")

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                selected_output_dir({"output_dir": "media/voiceovers/qwen"}),
                "media/voiceovers/qwen",
            )

    def test_write_voice_clone_config(self):
        env = {
            "FLAMING_HORSE_TTS_BACKEND": "mlx",
            "FLAMING_HORSE_MLX_PYTHON": "/env/mlx/python",
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "voice_clone_config.json"
            with patch.dict(os.environ, env, clear=True):
                write_voice_clone_config(path)
            self.assertIn('"backend": "mlx"', path.read_text(encoding="utf-8"))

    def test_cli_reports_missing_worker_python_without_traceback(self):
        env = {"FLAMING_HORSE_TTS_BACKEND": "mlx"}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "voice_clone_config.json"
            with (
                patch.dict(os.environ, env, clear=True),
                patch.object(
                    sys,
                    "argv",
                    ["tts_backend_config.py", "--write-voice-config", str(path)],
                ),
                patch("sys.stderr", new_callable=StringIO) as stderr,
            ):
                self.assertEqual(main(), 2)

            self.assertIn("ERROR: Missing MLX worker Python", stderr.getvalue())
            self.assertIn(".env.example", stderr.getvalue())
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
