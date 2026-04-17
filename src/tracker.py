#!/usr/bin/env python3
"""
fgphoto — Instagram Follower Tracker
Main entry point that orchestrates the tracking workflow.
"""

import webbrowser

from .config import OUTPUT_HTML
from .processor import process_snapshots
from .storage import load_followers_dict
from .generator import generate_html


def main():
    """Main workflow: process snapshots → generate dashboard → open in browser."""
    print("\n🚀 Starting Instagram Follower Tracker\n")

    # 1. Process new snapshots
    history = process_snapshots()

    # 2. Load followers state
    followers_dict = load_followers_dict()

    # 3. Generate HTML
    html = generate_html(history)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"\n  ✓ Dashboard saved → {OUTPUT_HTML}")

    # 4. Open in browser
    webbrowser.open(OUTPUT_HTML.as_uri())


if __name__ == "__main__":
    main()
