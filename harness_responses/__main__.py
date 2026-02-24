"""
CLI entry point for harness_responses.

Allows invocation via: python3 -m harness_responses
"""

import sys

from harness_responses.cli import main

if __name__ == "__main__":
    sys.exit(main())
