#!/usr/bin/env python3
"""Tests for scripts/qwen_tts_mediator.py."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import qwen_tts_mediator  # noqa: E402


class TestQwenTtsMediator(unittest.TestCase):
    def test_mlx_python_requires_backend_specific_env(self):
        with patch.dict(os.environ, {"PYTHON": "/wrong/orchestrator/python"}, clear=True):
            with self.assertRaisesRegex(ValueError, "Missing MLX worker Python"):
                qwen_tts_mediator._mlx_python()

    def test_mlx_python_uses_backend_specific_env(self):
        with patch.dict(
            os.environ,
            {"FLAMING_HORSE_MLX_PYTHON": "/env/mlx/python"},
            clear=True,
        ):
            self.assertEqual(qwen_tts_mediator._mlx_python(), "/env/mlx/python")


if __name__ == "__main__":
    unittest.main()
