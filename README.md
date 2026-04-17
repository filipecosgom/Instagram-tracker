# fgphoto — Instagram Follower Tracker

Tracks weekly follower changes for @fgphoto_ using Instagram data exports.
Generates a self-contained `dashboard.html` — no server, no dependencies beyond Python.

---

## Setup (first time only)

No installs needed. Python's standard library handles everything.

```
instagram-tracker/
  tracker.py
  snapshots/
    input/       ← drop your Instagram export ZIPs here
    processed/   ← script moves processed ZIPs here automatically
    history.json ← built up over time, do not delete
  dashboard.html ← generated output, opens automatically
```

---

## Weekly workflow

**Step 1 — Request your Instagram export**

Instagram → Settings → Your activity → Download your information
- Format: **JSON**
- Date range: All time
- Categories: select only **Followers and following**

Meta usually delivers the ZIP within a few minutes by email.

**Step 2 — Drop the ZIP into the input folder**

Place it in `snapshots/input/`. Rename it to include the date for cleaner tracking, e.g.:

```
instagram-2025-04-17.zip
```

If the filename has no date, the script uses the file's modification date.

**Step 3 — Run the script**

```bash
python tracker.py
```

The script:
1. Reads every new ZIP in `snapshots/input/`
2. Compares against the previous snapshot
3. Shows gained/lost in the terminal
4. Moves processed ZIPs to `snapshots/processed/`
5. Updates `snapshots/history.json`
6. Generates and opens `dashboard.html`

---

## Dashboard features

- **Stats bar** — total followers, gained, lost, net change vs. previous snapshot
- **Growth chart** — line chart of total followers across all snapshots
- **Snapshot selector** — view gained/lost detail for any past week
- **History table** — all snapshots at a glance with pill badges
- **Self-contained** — `dashboard.html` has no external dependencies once generated

---

## Notes

- The first snapshot is a baseline — gained/lost will show as 0. Differences appear from the second snapshot onward.
- `history.json` is the source of truth. Don't delete it. Back it up if you care about the history.
- If you accidentally process a ZIP twice, the script detects the duplicate date and skips it.
- The script reads multiple `followers_N.json` files if Instagram splits large exports.
