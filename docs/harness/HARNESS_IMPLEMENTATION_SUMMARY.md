# Harness Implementation Summary

`harness_responses/` is the live harness.

Each phase composes a prompt, invokes the local Grok Build CLI, validates the
staged JSON response with the phase Pydantic schema, and lets the parser promote
validated artifacts.

Runtime contract:

```text
Grok may read repository and project files.
Grok writes one staged JSON file under the project log directory.
The parser owns canonical artifact writes.
The orchestrator owns phase transitions.
```
