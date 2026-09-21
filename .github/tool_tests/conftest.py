"""Pytest configuration for the isolated .github/tools test suite."""
import sys
from pathlib import Path

# Ensure the tools directory is on sys.path so `import build_and_publish` etc. work.
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
