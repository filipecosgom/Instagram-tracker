"""Parse Instagram export ZIPs and extract usernames."""

import json
import re
import zipfile
from datetime import datetime
from pathlib import Path


def extract_usernames(zip_path: Path) -> set:
    """Extract usernames from Instagram export ZIP.

    Searches for followers JSON files in connections/followers_and_following/
    and extracts all usernames from string_list_data entries.
    """
    usernames = set()

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

        # Find all followers JSON files
        follower_files = [
            n
            for n in names
            if "connections/followers_and_following" in n.lower()
            and "followers" in n.lower()
            and n.endswith(".json")
            and "following" not in Path(n).name.lower()
        ]

        if not follower_files:
            print(f"  ⚠  No followers JSON found in {zip_path.name}")
            print(f"     Files in ZIP: {names}")
            return usernames

        for fname in follower_files:
            print(f"     📦 Reading {fname}")

            try:
                with zf.open(fname) as f:
                    data = json.load(f)
            except Exception as e:
                print(f"  ⚠  Failed to read {fname} in {zip_path.name}: {e}")
                continue

            entries = []
            if isinstance(data, list):
                entries = data
            elif isinstance(data, dict):
                for key in ("relationships_followers", "followers", "data"):
                    if key in data:
                        entries = data[key]
                        break
            else:
                print(f"  ⚠  Unexpected JSON type in {fname}")
                continue

            extracted = 0
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                sld = entry.get("string_list_data", [])
                if not isinstance(sld, list):
                    continue
                for item in sld:
                    if isinstance(item, dict) and "value" in item:
                        usernames.add(item["value"])
                        extracted += 1

            print(f"  ✅ Extracted {extracted} usernames from {fname}")

    return usernames


def get_snapshot_date(zip_path: Path) -> str:
    """Extract date from ZIP filename or fallback to modification time.

    Looks for YYYY-MM-DD or YYYY_MM_DD or YYYY-MM-DD pattern.
    Falls back to file modification time if not found.
    """
    match = re.search(r"(\d{4})[_\-]?(\d{2})[_\-]?(\d{2})", zip_path.stem)
    if match:
        y, m, d = match.groups()
        return f"{y}-{m}-{d}"
    mtime = zip_path.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
