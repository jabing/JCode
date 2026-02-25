"""
JCode CLI Entry Point
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.commands import jcode

def main():
    """Main CLI entry point."""
    jcode()

if __name__ == "__main__":
    main()
