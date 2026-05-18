#!/usr/bin/env python3
"""Tests for flaming_horse_voice/mlx_tts_service.py."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICE_PATH = REPO_ROOT / "flaming_horse_voice" / "mlx_tts_service.py"


def load_service_module(output_dir: Path):
    mlx_pkg = types.ModuleType("mlx")
    mlx_core = types.ModuleType("mlx.core")
    mlx_audio_pkg = types.ModuleType("mlx_audio")
    tts_pkg = types.ModuleType("mlx_audio.tts")
    generate_mod = types.ModuleType("mlx_audio.tts.generate")
    utils_mod = types.ModuleType("mlx_audio.tts.utils")
    soundfile_mod = types.ModuleType("soundfile")

    generate_mod.generate_audio = lambda *args, **kwargs: None
    utils_mod.load_model = lambda model_id: object()
    soundfile_mod.read = lambda path: ([0.0], 24000)

    modules = {
        "mlx": mlx_pkg,
        "mlx.core": mlx_core,
        "mlx_audio": mlx_audio_pkg,
        "mlx_audio.tts": tts_pkg,
        "mlx_audio.tts.generate": generate_mod,
        "mlx_audio.tts.utils": utils_mod,
        "soundfile": soundfile_mod,
    }

    spec = importlib.util.spec_from_file_location("mlx_tts_service_under_test", SERVICE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SERVICE_PATH}")
    module = importlib.util.module_from_spec(spec)
    env = {
        "MLX_OUTPUT_DIR": str(output_dir),
        "MLX_REF_AUDIO": str(output_dir / "voice.flac"),
    }
    with patch.dict(sys.modules, modules), patch.dict(os.environ, env, clear=True):
        spec.loader.exec_module(module)
    return module


class TestMlxTtsService(unittest.TestCase):
    def test_ref_text_env_value_avoids_file_lookup(self):
        with tempfile.TemporaryDirectory() as td:
            module = load_service_module(Path(td))
            self.assertEqual(module.resolve_ref_text("/missing/ref.flac", "hello"), "hello")

    def test_missing_ref_text_file_reports_configuration_error(self):
        with tempfile.TemporaryDirectory() as td:
            module = load_service_module(Path(td))
            with self.assertRaisesRegex(ValueError, "Missing MLX reference transcript"):
                module.resolve_ref_text(str(Path(td) / "voice.flac"), "")

    def test_ref_text_uses_path_suffix(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "voice.flac"
            transcript = Path(td) / "voice.txt"
            transcript.write_text("from file\n", encoding="utf-8")
            module = load_service_module(Path(td))
            self.assertEqual(module.resolve_ref_text(str(base), ""), "from file")


if __name__ == "__main__":
    unittest.main()
