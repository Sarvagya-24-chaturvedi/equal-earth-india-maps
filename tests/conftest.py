"""Pytest fixtures and environment configuration."""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure writable matplotlib cache during tests
os.environ.setdefault("MPLCONFIGDIR", str(ROOT_DIR / ".mpl_cache"))
