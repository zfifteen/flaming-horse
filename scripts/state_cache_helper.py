#!/usr/bin/env python3
"""
Efficient state cache helper to reduce subprocess spawning.

This module provides in-memory caching of project state to minimize
JSON file reads/writes and subprocess spawns in build_video.sh.

Usage from bash:
    # Load state into cache
    eval "$(python3 state_cache_helper.py load /path/to/project_state.json)"
    
    # Access cached values
    echo "$STATE_PHASE"
    echo "$STATE_RUN_COUNT"
    echo "$STATE_NEEDS_REVIEW"
    
    # Increment run count
    python3 state_cache_helper.py increment /path/to/project_state.json
    
    # Invalidate cache when external changes occur
    python3 state_cache_helper.py invalidate
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime


def load_state(state_file: Path) -> dict:
    """Load and return state from file."""
    with open(state_file, 'r') as f:
        return json.load(f)


def save_state(state_file: Path, state: dict) -> None:
    """Save state to file."""
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)


def export_bash_vars(state: dict) -> None:
    """Export state fields as bash variables."""
    import shlex
    # Export commonly accessed fields with proper shell escaping
    print(f"export STATE_PHASE={shlex.quote(str(state['phase']))}")
    print(f"export STATE_RUN_COUNT={shlex.quote(str(state['run_count']))}")
    print(f"export STATE_NEEDS_REVIEW={shlex.quote(str(state['flags'].get('needs_human_review', False)))}")
    print(f"export STATE_CURRENT_SCENE_INDEX={shlex.quote(str(state.get('current_scene_index', 0)))}")
    print(f"export STATE_CACHE_VALID='1'")


def cmd_load(args):
    """Load state and export as bash variables."""
    if len(args) < 2:
        print("Error: Missing state file path", file=sys.stderr)
        sys.exit(1)
    
    state_file = Path(args[1])
    if not state_file.exists():
        print(f"Error: State file not found: {state_file}", file=sys.stderr)
        sys.exit(1)
    
    state = load_state(state_file)
    export_bash_vars(state)


def cmd_increment(args):
    """Increment run_count and update timestamp."""
    if len(args) < 2:
        print("Error: Missing state file path", file=sys.stderr)
        sys.exit(1)
    
    state_file = Path(args[1])
    state = load_state(state_file)
    
    state['run_count'] += 1
    state['updated_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    save_state(state_file, state)
    # Re-export updated values
    export_bash_vars(state)


def cmd_invalidate(args):
    """Invalidate cache (unset bash variables)."""
    print("export STATE_CACHE_VALID='0'")
    print("unset STATE_PHASE STATE_RUN_COUNT STATE_NEEDS_REVIEW STATE_CURRENT_SCENE_INDEX")


def cmd_get_field(args):
    """Get a specific field from state."""
    if len(args) < 3:
        print("Error: Missing state file path or field name", file=sys.stderr)
        sys.exit(1)
    
    state_file = Path(args[1])
    field_path = args[2]  # e.g., "phase" or "flags.needs_human_review"
    
    state = load_state(state_file)
    
    # Navigate nested fields
    value = state
    for key in field_path.split('.'):
        if isinstance(value, dict):
            value = value.get(key)
        else:
            value = None
            break
    
    if value is not None:
        print(value)
    else:
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    commands = {
        'load': cmd_load,
        'increment': cmd_increment,
        'invalidate': cmd_invalidate,
        'get': cmd_get_field,
    }
    
    if cmd in commands:
        commands[cmd](sys.argv[1:])
    else:
        print(f"Error: Unknown command: {cmd}", file=sys.stderr)
        print("Valid commands: load, increment, invalidate, get", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
