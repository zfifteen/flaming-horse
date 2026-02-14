#!/usr/bin/env python3
"""
Estimate beats for narration script.
Usage: python scripts/estimate_beats.py <narration_key> <text>
"""

import sys
import re

if len(sys.argv) < 3:
    print("Usage: python estimate_beats.py <key> <text>")
    sys.exit(1)

key = sys.argv[1]
text = sys.argv[2]


def estimate_beats(text):
    words = len(text.split())
    return words // 3  # Simple estimate: 3 beats per ~words


beats = estimate_beats(text)
print(f"Estimated beats for {key}: {beats}")
