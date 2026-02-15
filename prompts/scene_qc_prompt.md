You are executing a dedicated scene quality-control pass for this project.

Working directory: {{PROJECT_DIR}}
State file: {{STATE_FILE}}

Primary instructions:
- Read and follow docs/SCENE_QC_AGENT_PROMPT.md exactly (from the repo).
- Validate and patch scene files listed below (from project_state.json):
{{SCENE_FILES}}
- Keep creative intent; fix timing sync and overlap/layout defects.
- Do NOT edit project_state.json.
- **MANDATORY**: Write a report file named `scene_qc_report.md` in this directory summarizing all changes.

**CRITICAL FILE EDITING RULES**:
1. When writing Python code to files, use ACTUAL newlines, not escaped sequences.
2. DO NOT write literal `\\n` characters (backslash-backslash-n) into Python files.
3. Python files must contain real line breaks between statements.
4. Test: if you see `\\n` in your output, you're doing it wrong.
5. Example CORRECT:
   ```python
   self.wait(0.5)
   self.play(FadeIn(obj))
   ```
6. Example WRONG (causes SyntaxError):
   ```python
   self.wait(0.5)\\nself.play(FadeIn(obj))
   ```

Attached files include:
- project_state.json

Begin now.
