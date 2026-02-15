# Scene Training Examples

This directory is the training corpus for the `training` phase.

- `good/foundations/`: simple baseline patterns for intro/outro scenes.
- `good/advanced/`: multi-step choreography patterns for middle scenes.
- `bad/`: anti-patterns the scene-writing agent must avoid.

Use these files to extract concrete rules before `build_scenes`.

## Complexity Profile (Mandatory)

- `simple` profile (usually intro or recap):
  - 3 to 5 animation events.
  - Focus on clarity and quick orientation.
  - Minimal object count and low visual density.
- `complex` profile (usually middle instructional scenes):
  - 8 to 12 animation events.
  - Must include staged build, at least one transform-style transition, and at least one emphasis animation.
  - Explicit cleanup between segments.

## Scene Role Mapping (Default)

- First scene: use `simple` unless plan marks it high complexity.
- Last scene: use `simple` unless recap explicitly requires a full worked example.
- All middle scenes: use `complex` by default.

## Core Expectations

- Keep a strict layout sequence: title, subtitle, then diagram/content.
- Use explicit transitions (`FadeOut`, `FadeTransform`) before introducing a new dense layer.
- Keep no more than two active non-persistent content layers.
- Use `safe_position()` after every `.next_to(...)` and `safe_layout(...)` for 2+ siblings.
- Never place a new center headline while bullets/diagram content is still visible.
