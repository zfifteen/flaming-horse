#!/usr/bin/env python3
"""Tests for scripts/tts_backend_config.py."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from tts_backend_config import (  # noqa: E402
    DEFAULT_MLX_MODEL_ID,
    selected_model_id,
    selected_tts_backend,
    selected_worker_python_raw,
)


class TestTtsBackendConfig(unittest.TestCase):
    def test_mlx_backend_uses_mlx_python_not_qwen_python(self):
        cfg = {
            "backend": "mlx",
            "qwen_python": "/missing/qwen/python",
            "model_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
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

    def test_qwen_backend_uses_qwen_python(self):
        cfg = {
            "backend": "qwen",
            "qwen_python": "/qwen/.venv/bin/python",
            "model_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        }
        with patch.dict(os.environ, {"FLAMING_HORSE_TTS_BACKEND": "qwen"}, clear=True):
            self.assertEqual(selected_tts_backend(), "qwen")
            self.assertEqual(
                selected_worker_python_raw(cfg, "qwen"),
                "/qwen/.venv/bin/python",
            )
            self.assertEqual(
                selected_model_id(cfg, "qwen"),
                "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            )


if __name__ == "__main__":
    unittest.main()
