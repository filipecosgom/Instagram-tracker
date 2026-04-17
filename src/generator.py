"""Generate HTML dashboard with injected data."""

import json

from .config import ENCODING, TEMPLATE_FILE


def generate_html(history: list) -> str:
    """Generate dashboard HTML by injecting snapshot data into template.

    Args:
        history: List of snapshot entries with date, total, gained, lost, followers.

    Returns:
        Complete HTML string ready to be written to file.

    Raises:
        FileNotFoundError: If template file doesn't exist.
    """
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_FILE}")

    template = TEMPLATE_FILE.read_text(encoding=ENCODING)
    data_json = json.dumps(history, indent=2, ensure_ascii=False)
    html = template.replace("__DATA_PLACEHOLDER__", data_json)
    return html
