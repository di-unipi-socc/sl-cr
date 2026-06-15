"""Configuration objects and default paths for CR experiments."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAIN_PL = Path(__file__).resolve().parent / "prolog" / "main.pl"
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results"
