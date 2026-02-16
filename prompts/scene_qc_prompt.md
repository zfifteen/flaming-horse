You are executing a dedicated scene quality-control pass for this project.

Working directory: {{PROJECT_DIR}}
State file: {{STATE_FILE}}

Primary instructions:
- Read and follow docs/SCENE_QC_AGENT_PROMPT.md exactly (from the repo).
- Validate and patch scene files listed below (from project_state.json):
{{SCENE_FILES}}
- Keep creative intent; fix timing sync and overlap/layout defects.
- Treat underwhelming sparse scenes as defects: if a scene is mostly static/black with one late trivial animation, rewrite the scene body to an explainer-slide cadence.
- For non-math scenes, require progressive bullet reveals plus evolving topic-specific visuals over the full narration duration.
- Do NOT edit project_state.json.
- Write a report file named scene_qc_report.md in this directory.

Attached files include:
- project_state.json

Begin now.
