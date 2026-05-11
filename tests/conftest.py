"""Shared pytest fixtures and path setup."""

import sys
from pathlib import Path

# Make the repo root importable so tests can `from tools import demo_loader`.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
