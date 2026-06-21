"""EYES Workbench — HTML dashboard, job orchestrator, and saved workflow progress."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = Path(__file__).resolve().parent
JOBS_DIR = DASHBOARD_DIR / "jobs"
DATA_DIR = DASHBOARD_DIR / "data"
STATE_PATH = DATA_DIR / "state.json"
