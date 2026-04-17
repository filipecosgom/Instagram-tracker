#!/usr/bin/env python3
"""
fgphoto — Instagram Follower Tracker
--------------------------------------
Reads Instagram export ZIPs from snapshots/input/
Compares consecutive snapshots
Generates a self-contained dashboard.html
"""

import json
import zipfile
import re
import webbrowser
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────
INPUT_DIR = Path("snapshots/input")
PROCESSED_DIR = Path("snapshots/processed")
HISTORY_FILE = Path("snapshots/history.json")
OUTPUT_HTML = Path("dashboard.html").resolve()
MASTER_FILE = Path("snapshots/master_followers.json")
FOLLOWERS_FILE = Path("snapshots/master_followers.json")


# ── Process Master Followers List ──────────────────────────────────────────────
def load_master() -> set:
    if MASTER_FILE.exists():
        data = json.loads(MASTER_FILE.read_text(encoding="utf-8"))
        return set(data) if isinstance(data, list) else set()
    return set()


def save_master(followers: set):
    MASTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    MASTER_FILE.write_text(
        json.dumps(sorted(followers), indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── Create the follower model state ────────────────────────────────────────────
def load_followers_dict() -> dict:
    """Carrega o estado de todos os seguidores.
    Formato: { "username": { "first_seen": "2025-10-20", "last_seen": "2026-04-16", "status": "active" } }
    """
    if FOLLOWERS_FILE.exists():
        data = json.loads(FOLLOWERS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    return {}


def save_followers_dict(followers: dict):
    FOLLOWERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    FOLLOWERS_FILE.write_text(
        json.dumps(followers, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── Instagram JSON parsing ─────────────────────────────────────────────────────
def extract_usernames(zip_path: Path) -> set:
    usernames = set()

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

        # ── todos os ficheiros "followers" dentro de followers_and_following ──
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
    match = re.search(r"(\d{4})[_\-]?(\d{2})[_\-]?(\d{2})", zip_path.stem)
    if match:
        y, m, d = match.groups()
        return f"{y}-{m}-{d}"
    mtime = zip_path.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")


# ── History management ─────────────────────────────────────────────────────────
def load_history() -> list:
    if HISTORY_FILE.exists():
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    return []


def save_history(history: list):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── Snapshot processing ────────────────────────────────────────────────────────
def process_snapshots() -> list:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    history = load_history()
    followers_dict = load_followers_dict()  # { "user": { ... } }
    existing_dates = {entry["date"] for entry in history}
    now = datetime.now().strftime("%Y-%m-%d")

    new_count = 0

    for zip_path in sorted(INPUT_DIR.glob("*.zip")):
        date = get_snapshot_date(zip_path)

        if date in existing_dates:
            print(f"  ↩  {zip_path.name} already processed ({date}), skipping")
            continue

        print(f"  📦 Processing {zip_path.name} → {date}")
        current_snap = extract_usernames(zip_path)

        if not current_snap:
            print("  ⚠  No usernames extracted, skipping")
            continue

        # existing_snap = usernames “activos” no dicionário (status != "lost")
        active_prev = {
            u
            for u, info in followers_dict.items()
            if info.get("status", "active") != "lost"
        }

        # 1. novos e perdidos vs snapshot atual
        new = current_snap - active_prev
        lost = active_prev - current_snap

        # 2. atualizar o dicionário de seguidores
        for u in current_snap:
            if u not in followers_dict:
                followers_dict[u] = {
                    "first_seen": date,
                    "last_seen": date,
                    "status": "active",
                }
            else:
                followers_dict[u]["last_seen"] = date
                followers_dict[u]["status"] = "active"

        for u in lost:
            if u in followers_dict:
                followers_dict[u]["status"] = "lost"

        # 3. guardar na history (para o dashboard)
        history.append(
            {
                "date": date,
                "total": len(current_snap),
                "gained": sorted(new),
                "lost": sorted(lost),
                "followers": sorted(current_snap),
            }
        )

        existing_dates.add(date)
        new_count += 1

        dest = PROCESSED_DIR / zip_path.name
        zip_path.rename(dest)
        print(f"     ✓ Moved to snapshots/processed/")

    if new_count == 0:
        print("  No new snapshots to process.")
    else:
        save_history(history)
        save_followers_dict(followers_dict)
        print(f"\n  ✓ History updated ({len(history)} snapshots)")
        print(
            f"  ✓ Master followers updated ({len([u for u, i in followers_dict.items() if i['status'] == 'active'])} active)"
        )

    return history


# ── HTML generation ────────────────────────────────────────────────────────────
def generate_html(history: list, followers_dict: dict) -> str:
    """Generate the dashboard HTML by reading template and injecting data."""
    assets_dir = Path("assets")
    template_path = assets_dir / "dashboard.html"

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    template = template_path.read_text(encoding="utf-8")
    data_json = json.dumps(history, indent=2, ensure_ascii=False)
    html = template.replace("__DATA_PLACEHOLDER__", data_json)
    return html


def main():
    history = process_snapshots()  # 1
    followers_dict = load_followers_dict()  # 2

    # 3
    html = generate_html(history, followers_dict)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  ✓ Saved → {OUTPUT_HTML}")
    webbrowser.open(OUTPUT_HTML.as_uri())


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    main()
