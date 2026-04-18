"""Generate HTML dashboard with injected data."""

import json

from .config import ENCODING, TEMPLATE_FILE


def generate_html(history: list, total_active: int = 0, followers_dict: dict = None) -> str:
    """Generate dashboard HTML by injecting snapshot data into template.

    Args:
        history: List of snapshot entries with date, total, gained, lost, followers.
        total_active: Current count of active followers from master_followers.json.
        followers_dict: Master followers dictionary with profile images.

    Returns:
        Complete HTML string ready to be written to file.

    Raises:
        FileNotFoundError: If template file doesn't exist.
    """
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_FILE}")

    if followers_dict is None:
        followers_dict = {}

    template = TEMPLATE_FILE.read_text(encoding=ENCODING)
    # Create data object with both history and metadata
    data = {
        "snapshots": history,
        "totalActive": total_active,
        "followers": followers_dict
    }
    data_json = json.dumps(data, indent=2, ensure_ascii=False)
    html = template.replace("__DATA_PLACEHOLDER__", data_json)
    return html


