Please review all scene files for render-blocking runtime failures only.

**Scene Files**:

{{all_scenes}}

Review each file for render-blocking runtime failures only and:
1. Flag rewrite_required=true only when a runtime error would prevent Manim scene generation
2. Flag rewrite_required=false for all non-blocking issues (including style/layout/timing preferences)
3. Generate scene_qc_report.md

Output only the QC report. Do not output modified scene files.
