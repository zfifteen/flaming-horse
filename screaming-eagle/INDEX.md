I am designing a training phase for the scene_repair system to add statefulness and accumulated learning from failures. Instead of making the prompt omniscient, I will make the system learn from its own debugging experience by tracking errors, extracting generalizable lessons, and injecting learned context into future prompts. This shifts from reactive error-fixing to proactive knowledge accumulation to break the retry loop where the model repeats the same mistakes on successive repair attempts.

1. Gather evidence - Continue reviewing logs, error patterns, and prompt configurations
2. Analyze the evidence - Identify systemic failure modes in scene_repair
3. Formulate a hypothesis - e.g., "The model lacks debugging methodology + memory"
4. Test the hypothesis - Verify by examining whether errors repeat and why prompts don't prevent them
5. Iterate on the hypothesis - Refine until the error condition is reproducible (e.g., demonstrate font_weight error on fresh scene)
6. Draft an implementation plan - Design the training phase architecture
7. Gather peer reviews - Get feedback on the implementation plan
8. Finalize the implementation plan - Incorporate feedback
9. Capture as GitHub issue - Document the complete spec for the training phase
