# Integration Handoff — Ready for Big D

**Date**: 2024-02-11  
**Status**: ✅ APPROVED by Claude Perplexity Reviewer  
**Location**: `~/IdeaProjects/flaming-horse/incremental_builder/`

---

## What's Been Built

A complete bash-driven agentic loop system for iterative Manim video production:

- **State machine**: 7 phases (plan → review → narration → build_scenes → final_render → assemble → complete)
- **Lock file protection**: Prevents concurrent builds
- **JSON state management**: Python-based (no jq dependency)
- **Reference docs integration**: Ready to attach your 4 Manim guides
- **Error handling**: Comprehensive validation, backup/restore, human review flags
- **Example files**: Complete templates for plan, narration, voice config

### File Inventory

```
✅ build_video.sh              (9.4 KB, 307 lines) - Main orchestrator
✅ system_prompt.md            (14 KB, 454 lines)  - Agent instructions
✅ README.md                   (2.2 KB, 75 lines)  - User documentation
✅ new_project.sh              (901 B, 40 lines)   - Project creator
✅ reset_phase.sh              (1.2 KB, 50 lines)  - Phase reset utility
✅ validate_scaffold.sh        (2.5 KB, 82 lines)  - Validation checker
✅ example_project/*.example   (3 files, 5.4 KB)   - Templates
✅ reference_docs/             (4 placeholders)    - Your docs go here
✅ IMPLEMENTATION_SUMMARY.md   (Summary document)
```

---

## 🔴 THREE QUESTIONS FOR BIG D

### Question 1: Reference Documentation Paths

**What I need**: Full paths to your four Manim reference files.

**Expected locations** (based on Space context):
```
~/Documents/Space/manim_content_pipeline.md
~/Documents/Space/manim_voiceover.md
~/Documents/Space/manim_template.py.txt
~/Documents/Space/manim_config_guide.md
```

**What I'll do with them**: Create symlinks in `reference_docs/` so the agent has access:
```bash
cd ~/IdeaProjects/flaming-horse/incremental_builder/reference_docs
ln -sf <your_path>/manim_content_pipeline.md .
ln -sf <your_path>/manim_voiceover.md .
ln -sf <your_path>/manim_template.py.txt .
ln -sf <your_path>/manim_config_guide.md .
```

**Please provide**:
```
Path 1 (manim_content_pipeline.md): _______________________
Path 2 (manim_voiceover.md):        _______________________
Path 3 (manim_template.py.txt):     _______________________
Path 4 (manim_config_guide.md):     _______________________
```

---

### Question 2: AI Agent CLI Tool

**What I need**: The exact command you use to invoke Claude from bash.

**Options I'm aware of**:

A) **Anthropic Official CLI** (`claude`)
```bash
claude \
  --model claude-sonnet-4-20250514 \
  --system "$(cat system_prompt.md)" \
  --attach file1.md --attach file2.md \
  --prompt "Your instruction here"
```

B) **Simon Willison's LLM** (`llm`)
```bash
llm prompt claude-sonnet-4 \
  --system "$(cat system_prompt.md)" \
  -a file1.md -a file2.md \
  "Your instruction here"
```

C) **Custom Python Script**
```bash
python3 agent_runner.py \
  --system system_prompt.md \
  --attach file1.md \
  --attach file2.md \
  --prompt "Your instruction"
```

D) **Something else?**

**Please provide**:
```
Tool name/command: _______________________
Syntax for system prompt: _______________________
Syntax for attaching files: _______________________
Syntax for main prompt: _______________________
```

**Example**: If you use `claude`, I need to know:
- Is it `--attach` or `-a` for files?
- Is it `--system` or `--system-prompt`?
- Does it support `--working-dir`?

---

### Question 3: ElevenLabs API Key

**What I need**: Confirmation that you have the key set.

**Current configuration in build_video.sh**:
- Voice ID: `rBgRd5IfS6iqrGfuhlKR`
- Model: `eleven_multilingual_v2`

**Setup required**:
```bash
export ELEVENLABS_API_KEY='sk-...your-key...'

# For persistence in ~/.zshrc:
echo "export ELEVENLABS_API_KEY='sk-...your-key...'" >> ~/.zshrc
source ~/.zshrc
```

**Please confirm**:
- [ ] I have the API key
- [ ] It's exported in my shell environment
- [ ] The voice ID `rBgRd5IfS6iqrGfuhlKR` is correct

---

## What Happens After You Answer

### Step 1: I'll Create Symlinks
Based on your paths, I'll create the reference doc symlinks:
```bash
cd ~/IdeaProjects/flaming-horse/incremental_builder/reference_docs
ln -sf <your_provided_path_1> manim_content_pipeline.md
ln -sf <your_provided_path_2> manim_voiceover.md
# ... etc
```

### Step 2: I'll Implement Agent Invocation
Based on your CLI tool, I'll replace the TODO in `invoke_agent()`:
```bash
invoke_agent() {
  local phase="$1"
  local run_num="$2"
  
  # Your actual CLI command here
  your-cli-tool \
    --system "$(cat ${SCRIPT_DIR}/system_prompt.md)" \
    ${context_files} \
    --attach "$STATE_FILE" \
    --prompt "Execute phase: ${phase}..." \
    --working-dir "$PROJECT_DIR"
}
```

### Step 3: We'll Test
```bash
# Create test project
./new_project.sh test_gravity ~/manim_projects

# Run one phase manually to verify agent integration
./build_video.sh ~/manim_projects/test_gravity
```

---

## Validation Status

Current validation (run `./validate_scaffold.sh`):
```
✅ 14/14 core files present
✅ All scripts executable
✅ Example files complete
⏳ Reference docs: Awaiting symlinks (your paths needed)
⏳ Agent invocation: Awaiting CLI tool name
⏳ API key: Awaiting confirmation
```

---

## Quick Reference

### Project Creation
```bash
./new_project.sh <project_name> <location>
```

### Build Execution
```bash
./build_video.sh <project_directory>
```

### Phase Reset (for debugging)
```bash
./reset_phase.sh <project_directory> <phase_name>
```

### Valid Phases
- `plan` - Generate video outline
- `review` - Validate plan
- `narration` - Create scripts
- `build_scenes` - Build scenes incrementally
- `final_render` - Production render with ElevenLabs
- `assemble` - Concatenate scenes
- `complete` - Finalize

---

## Ready for Your Input!

Once you provide:
1. ✅ The four reference doc paths
2. ✅ Your CLI tool name and syntax
3. ✅ API key confirmation

...I'll complete the integration and we can run a test build.

**Please reply with answers to the three questions above.** 🚀

---

**Built by**: Claude Sonnet 4.5 (scaffold) + Claude Sonnet 4.5 (Perplexity review)  
**For**: Big D' (Dionisio)  
**Project**: Incremental Manim Video Builder  
**Date**: February 11, 2024
