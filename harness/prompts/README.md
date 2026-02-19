# Prompt Directory

This directory is organized in pipeline order.

- `00_plan`
- `01_review`
- `02_narration`
- `04_build_scenes`
- `05_scene_qc`
- `06_scene_repair`
- `07_precache_voiceovers`
- `08_final_render`
- `09_assemble`
- `10_complete`

Each active LLM phase should define:
- `system.md`
- `user.md`
- `manifest.yaml`

Shared prompt fragments live under `_shared/`.
