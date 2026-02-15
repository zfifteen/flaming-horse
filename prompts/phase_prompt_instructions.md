INSTRUCTIONS:
1. Read project_state.json to understand the current state.
2. Execute ONLY the {{PHASE}} phase tasks as defined in the system prompt above.
3. For the plan phase: Generate plan.json exactly as specified in reference_docs/phase_plan.md. Use the Write tool to create the file at ./plan.json with JSON content. Ensure it has keys like title, topic_summary, and a scenes array with required fields (id, title, narration_key, etc.).
4. For other phases, use the Write or Edit tools to generate required files (e.g., narration_script.py, scene_*.py).
5. Do NOT edit project_state.json. The build pipeline owns state updates. Only generate required artifacts for the phase (plan.json, narration_script.py, scene_*.py).
6. If errors occur, do NOT edit state; instead, explain what failed in plain text.

IMPORTANT PATH NOTE:
- Your working directory is the project directory, which does NOT contain a ./scripts folder.
- If you need to scaffold a scene, run the scaffold tool via the absolute path below, e.g.:
  python3 "{{SCAFFOLD_PATH}}" --project . --scene-id <scene_id> --class-name <ClassName> --narration-key <key>

