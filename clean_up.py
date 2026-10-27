"""List accounts you follow that don't follow you back, from an Instagram JSON export.

Usage: python3 clean_up.py [exports/DD-MM-YY]
Writes unfollow.json into that date folder (default: the newest folder in exports/).
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPORTS = Path(__file__).resolve().parent / "exports"


def username_of(entry):
    """Older exports put the name in string_list_data[0].value, newer ones in title or only the href."""
    if not isinstance(entry, dict):
        return None, None
    sld = entry.get("string_list_data")
    item = sld[0] if isinstance(sld, list) and sld and isinstance(sld[0], dict) else {}
    href = item.get("href")
    name = item.get("value") or entry.get("title")
    if not name and isinstance(href, str):
        name = href.rstrip("/").rsplit("/", 1)[-1]
    name = name.strip().lstrip("@") if isinstance(name, str) else ""
    return (name or None), (href.rstrip("/") if isinstance(href, str) else None)


def load_accounts(entries, label, warnings):
    """Return {casefolded username: {username, profile_url}}, collapsing duplicates."""
    accounts, skipped = {}, 0
    for entry in entries:
        name, href = username_of(entry)
        if name is None:
            skipped += 1
            continue
        accounts.setdefault(name.casefold(), {"username": name, "profile_url": href})
    if skipped:
        warnings.append(f"{label}: skipped {skipped} malformed record(s)")
    if not accounts:
        warnings.append(f"{label}: list is empty, the export may be incomplete")
    return accounts


def compare(date_dir):
    lists = date_dir / "connections" / "followers_and_following"
    follower_files = sorted(lists.glob("followers_*.json"))
    following_file = lists / "following.json"
    if not follower_files or not following_file.exists():
        sys.exit(f"No followers_*.json / following.json in {lists}. Request the export in JSON format, not HTML.")

    warnings = []
    follower_entries = [e for f in follower_files for e in json.loads(f.read_text())]
    following_raw = json.loads(following_file.read_text())
    following_entries = following_raw.get("relationships_following", []) if isinstance(following_raw, dict) else following_raw

    followers = load_accounts(follower_entries, "followers", warnings)
    following = load_accounts(following_entries, "following", warnings)
    not_back = [following[k] for k in sorted(following.keys() - followers.keys())]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "local Instagram export",
        "source_dir": date_dir.name,
        "snapshot_note": "Snapshot of the export date; may be stale.",
        "counts": {"following": len(following), "followers": len(followers), "not_following_back": len(not_back)},
        "accounts": not_back,
        "warnings": warnings,
    }


def newest_export():
    dated = []
    for d in EXPORTS.iterdir() if EXPORTS.is_dir() else []:
        try:
            dated.append((datetime.strptime(d.name, "%d-%m-%y"), d))
        except ValueError:
            continue
    if not dated:
        sys.exit(f"No DD-MM-YY folders found in {EXPORTS}")
    return max(dated)[1]


def main(argv):
    date_dir = Path(argv[0]) if argv else newest_export()
    if not date_dir.is_dir():
        sys.exit(f"{date_dir} does not exist. Example: python3 clean_up.py exports/27-10-26")
    report = compare(date_dir)
    out = date_dir / "unfollow.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    c = report["counts"]
    print(f"Following {c['following']}, followers {c['followers']}, not following back {c['not_following_back']}")
    for w in report["warnings"]:
        print(f"warning: {w}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
