"""
CLI entry point for the Flaming Horse agent harness.

Allows invocation via: python3 -m harness
"""

import sys

from harness.cli import main

if __name__ == "__main__":
    sys.exit(main())
