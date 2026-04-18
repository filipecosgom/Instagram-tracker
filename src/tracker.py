#!/usr/bin/env python3
"""
fgphoto — Instagram Follower Tracker
Main entry point that orchestrates the tracking workflow.
"""

import sys
import webbrowser

from .config import OUTPUT_HTML
from .processor import process_snapshots
from .storage import load_followers_dict
from .generator import generate_html


def main():
    """Main workflow: process snapshots → generate dashboard → open in browser."""
    # Handle Windows console encoding
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n> Starting Instagram Follower Tracker\n")

    # 1. Process new snapshots
    history = process_snapshots()

    # 2. Load followers state
    followers_dict = load_followers_dict()

    # 3. Calculate active followers count
    total_active = len([u for u, i in followers_dict.items() if i["status"] == "active"])

    # 4. Generate HTML
    html = generate_html(history, total_active, followers_dict)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"\n  OK Dashboard saved -> {OUTPUT_HTML}")

    # 5. Open in browser
    webbrowser.open(OUTPUT_HTML.as_uri())


if __name__ == "__main__":
    main()

