Please review all scene files for render-blocking runtime failures only.

**Scene Files**:

{{all_scenes}}

Review each file for render-blocking runtime failures only and:
1. Flag rewrite_required=true only when a runtime error would prevent Manim scene generation
2. Flag rewrite_required=false for all non-blocking issues (including style/layout/timing preferences)
3. Generate scene_qc_report.md content as markdown

### Self-Check Before Output

- [ ] Every scene file listed in the input has an entry in the report.
- [ ] `rewrite_required: true` is set ONLY for render-blocking runtime failures.
- [ ] Style, timing, and layout issues are NOT flagged as rewrite_required.
- [ ] `report_markdown` is a non-empty markdown string.
- [ ] Output is exactly one JSON object with field `report_markdown`.

Output exactly one JSON object with required field `report_markdown`.
Do not output modified scene files.
