"""Process Instagram export snapshots and track changes."""

from pathlib import Path

from .config import INPUT_DIR, PROCESSED_DIR
from .parser import extract_usernames, get_snapshot_date
from .storage import load_history, save_history, load_followers_dict, save_followers_dict


def process_snapshots() -> list:
    """Process new snapshots from input directory.

    For each new ZIP file:
    1. Extract usernames
    2. Compare with previous active followers
    3. Track gained/lost followers
    4. Update followers state dictionary
    5. Move processed ZIP to processed directory

    Returns:
        Complete history of all processed snapshots.
    """
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    history = load_history()
    followers_dict = load_followers_dict()
    existing_dates = {entry["date"] for entry in history}

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

        # Get active followers from previous snapshots (status != "lost")
        active_prev = {
            u
            for u, info in followers_dict.items()
            if info.get("status", "active") != "lost"
        }

        # Calculate new and lost followers
        new = current_snap - active_prev
        lost = active_prev - current_snap

        # Update followers dictionary
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

        # Add to history for dashboard
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
        active_count = len([u for u, i in followers_dict.items() if i["status"] == "active"])
        print(f"\n  ✓ History updated ({len(history)} snapshots)")
        print(f"  ✓ Master followers updated ({active_count} active)")

    return history
