"""Configuration objects and default paths for CR experiments."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAIN_PL = Path(__file__).resolve().parent / "prolog" / "main.pl"
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results"


STEPS = 100
TIMEOUT = 300  # seconds

NODE_STORAGE = (10, 20)
COMPONENT_STORAGE = (4, 8)
NODE_STORAGE_MULTIPLIER = (0.25, 1.0)

LINK_LATENCY = (1, 10)
INTERACTION_LATENCY = (5, 50)
