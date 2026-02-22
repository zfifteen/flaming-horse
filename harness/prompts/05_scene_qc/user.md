## Purpose
Review all scene files for render-blocking runtime failures only.

## Inputs
Scene files:

{{all_scenes}}

## Required Output
Return exactly one JSON object with required field `report_markdown`.
- `report_markdown`: non-empty markdown string (content for scene_qc_report.md)
- Do NOT output modified scene files

## Hard Rules
- Flag `rewrite_required: true` ONLY for runtime errors that prevent Manim from rendering the scene
- Flag `rewrite_required: false` for all non-blocking issues (style, layout, timing, visual quality)
- Report every scene — even scenes with no issues

## Self-Check Before Responding
- [ ] Every scene file has an entry in the report
- [ ] `rewrite_required: true` is used only for genuine render-blocking failures
- [ ] `report_markdown` is non-empty
- [ ] Output is exactly one JSON object with `report_markdown` field
