INSTRUCTIONS:
1. Read project_state.json to understand the current state.
2. Execute ONLY the {{PHASE}} phase tasks as defined in the system prompt above.
3. File lifecycle is owned by the orchestrator. You must not create new files for phase artifacts.
4. For the plan phase: update existing ./plan.json exactly as specified in reference_docs/phase_plan.md. Use Edit only; do not use Write to create files. Keep required keys such as title, topic_summary, and scenes entries.
5. For narration/build_scenes: update only orchestrator-provided files (e.g., narration_script.py, target scene file). Use Edit only.
   - For build_scenes, do not run scaffold or shell infrastructure steps; only edit the orchestrator-provided target file and only inside `# SLOT_START:scene_body`.
6. If an expected phase artifact file is missing (plan.json, narration_script.py, target scene file), fail the phase and report the missing file in plain text. Do not create it.
7. Do NOT edit project_state.json. The build pipeline owns state updates.
8. If errors occur, do NOT edit state; instead, explain what failed in plain text.

IMPORTANT PATH NOTE:
- Your working directory is the project directory, which does NOT contain a ./scripts folder.
- Infrastructure tasks (scaffold/state management) are handled by the orchestrator; do not perform them from the agent.
