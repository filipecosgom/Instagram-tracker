"""Manage data persistence (load/save operations)."""

import json
from pathlib import Path

from .config import ENCODING, HISTORY_FILE, MASTER_FILE, FOLLOWERS_FILE


def load_history() -> list:
    """Load snapshot history from JSON file.

    Returns:
        List of snapshot entries or empty list if file doesn't exist.
    """
    if HISTORY_FILE.exists():
        data = json.loads(HISTORY_FILE.read_text(encoding=ENCODING))
        return data if isinstance(data, list) else []
    return []


def save_history(history: list) -> None:
    """Save snapshot history to JSON file."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False), encoding=ENCODING
    )


def load_followers_dict() -> dict:
    """Load followers state dictionary.

    Format: { "username": { "first_seen": "YYYY-MM-DD", "last_seen": "YYYY-MM-DD", "status": "active"|"lost" } }

    Returns:
        Dictionary of followers or empty dict if file doesn't exist.
    """
    if FOLLOWERS_FILE.exists():
        data = json.loads(FOLLOWERS_FILE.read_text(encoding=ENCODING))
        return data if isinstance(data, dict) else {}
    return {}


def save_followers_dict(followers: dict) -> None:
    """Save followers state dictionary to JSON file."""
    FOLLOWERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    FOLLOWERS_FILE.write_text(
        json.dumps(followers, indent=2, ensure_ascii=False), encoding=ENCODING
    )


def load_master() -> set:
    """Load master follower list.

    Returns:
        Set of usernames or empty set if file doesn't exist.
    """
    if MASTER_FILE.exists():
        data = json.loads(MASTER_FILE.read_text(encoding=ENCODING))
        return set(data) if isinstance(data, list) else set()
    return set()


def save_master(followers: set) -> None:
    """Save master follower list to JSON file."""
    MASTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    MASTER_FILE.write_text(
        json.dumps(sorted(followers), indent=2, ensure_ascii=False), encoding=ENCODING
    )
