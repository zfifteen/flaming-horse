#!/usr/bin/env python3
"""Tests for scripts/prepare_qwen_voice.py."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from prepare_qwen_voice import compute_fingerprint  # noqa: E402


class TestPrepareQwenVoice(unittest.TestCase):
    def test_fingerprint_uses_resolved_model_id(self):
        with tempfile.TemporaryDirectory() as td:
            ref_audio = Path(td) / "ref.wav"
            ref_text = Path(td) / "ref.txt"
            ref_audio.write_bytes(b"audio")
            ref_text.write_text("text\n", encoding="utf-8")
            cfg = {
                "model_id": "project/model",
                "device": "cpu",
                "dtype": "float32",
                "language": "English",
            }

            project_fp = compute_fingerprint(
                cfg,
                "mlx",
                "project/model",
                "/env/mlx/python",
                ref_audio,
                ref_text,
            )
            env_fp = compute_fingerprint(
                cfg,
                "mlx",
                "env/model",
                "/env/mlx/python",
                ref_audio,
                ref_text,
            )

            self.assertNotEqual(project_fp, env_fp)

    def test_fingerprint_changes_when_backend_changes(self):
        with tempfile.TemporaryDirectory() as td:
            ref_audio = Path(td) / "ref.wav"
            ref_text = Path(td) / "ref.txt"
            ref_audio.write_bytes(b"audio")
            ref_text.write_text("text\n", encoding="utf-8")
            cfg = {
                "model_id": "shared/model",
                "device": "cpu",
                "dtype": "float32",
                "language": "English",
            }

            qwen_fp = compute_fingerprint(
                cfg,
                "qwen",
                "shared/model",
                "/env/qwen/python",
                ref_audio,
                ref_text,
            )
            mlx_fp = compute_fingerprint(
                cfg,
                "mlx",
                "shared/model",
                "/env/qwen/python",
                ref_audio,
                ref_text,
            )

            self.assertNotEqual(qwen_fp, mlx_fp)

    def test_fingerprint_changes_when_worker_python_changes(self):
        with tempfile.TemporaryDirectory() as td:
            ref_audio = Path(td) / "ref.wav"
            ref_text = Path(td) / "ref.txt"
            ref_audio.write_bytes(b"audio")
            ref_text.write_text("text\n", encoding="utf-8")
            cfg = {
                "model_id": "shared/model",
                "device": "cpu",
                "dtype": "float32",
                "language": "English",
            }

            first_fp = compute_fingerprint(
                cfg,
                "mlx",
                "shared/model",
                "/env/mlx/python-a",
                ref_audio,
                ref_text,
            )
            second_fp = compute_fingerprint(
                cfg,
                "mlx",
                "shared/model",
                "/env/mlx/python-b",
                ref_audio,
                ref_text,
            )

            self.assertNotEqual(first_fp, second_fp)


if __name__ == "__main__":
    unittest.main()
