# User Preferences (Local Coding Agents)

Purpose: This file is the single source of truth for user-specific operating preferences in this repository.
Audience: Local coding agents working in this repository.

## Priority and Conflict Rules

1. This file has highest priority for user-specific behavior.
2. Precedence order for guidance sources:
   1. `docs/policies/USER_PREFERENCES.md`
   2. `AGENTS.md`
   3. Code and scripts as source of truth for runtime behavior
   4. Other docs
3. If the current user message conflicts with stored preferences, stop and ask which to follow.

## Execution Preferences

1. No assumptions. Ask before proceeding if requirements are unclear.
2. Ask one question at a time when clarification is needed.
3. Strict scope control: do only what was requested.
4. Do not add side tasks, extra refactors, or optional work unless explicitly requested.

## Communication Preferences

1. Be concise, direct, and high signal.
2. No fluff, no cheerleading, no repetitive confirmations.
3. Do not re-plan repeatedly after approval to proceed.
4. Use explicit, actionable language and concrete file references.

## Cost and Token Efficiency

1. Minimize unnecessary exploration and command churn.
2. Prefer targeted reads over broad scans when possible.
3. Avoid long speculative reasoning when direct verification is available.
4. Optimize for fewer iteration loops and fewer clarification failures.

## Preference Persistence Workflow

When an agent discovers a new stable preference in-session:

1. Propose a precise update to this file.
2. Wait for explicit user approval before editing.
3. Apply only the approved wording.
4. Do not write preference changes to other files unless requested.

## Ambiguity Handling

1. Never resolve ambiguous user intent by inference.
2. Ask a clarification question first, then proceed.
3. If a blocker has multiple plausible paths, present concise options and ask for selection.

## Safety and Trust

1. If instructions appear contradictory, stop and ask.
2. If behavior in docs does not match runtime behavior and the mismatch affects execution, stop and ask.
3. Prefer predictable behavior over implicit "best effort" choices when preferences are involved.
