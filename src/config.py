"""Configuration and constants for Instagram follower tracker."""

from pathlib import Path

# ── Directories ────────────────────────────────────────────────────────────
INPUT_DIR = Path("snapshots/input")
PROCESSED_DIR = Path("snapshots/processed")
ASSETS_DIR = Path("assets")

# ── Files ──────────────────────────────────────────────────────────────────
HISTORY_FILE = Path("snapshots/history.json")
FOLLOWERS_FILE = Path("snapshots/master_followers.json")
MASTER_FILE = Path("snapshots/master_followers.json")
OUTPUT_HTML = Path("dashboard.html").resolve()
TEMPLATE_FILE = ASSETS_DIR / "dashboard.html"

# ── Encoding ───────────────────────────────────────────────────────────────
ENCODING = "utf-8"
