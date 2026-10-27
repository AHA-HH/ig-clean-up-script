# ig-clean-up-script

Find the Instagram accounts you follow that don't follow you back, using Instagram's own data export. Runs locally — no login, no password, no network calls, and it never follows or unfollows anything.

Requires Python 3.10+ (no packages to install).

## 1. Download your data from Instagram

1. Go to <https://accountscenter.instagram.com/info_and_permissions/dyi/>
2. **Download or transfer information** → pick your Instagram account → **Some of your information**.
3. Tick only **Followers and following** → **Download to device**.
4. Set **Date range: All time** and **Format: JSON** (not HTML), then **Create files**.
5. Instagram emails you when the ZIP is ready (minutes to hours). Download and unzip it.

## 2. Put it in `exports/`

Create a folder named with the export date as `DD-MM-YY` and move the unzipped `connections` folder into it:

```text
exports/
└── 27-10-26/
    └── connections/
        └── followers_and_following/
            ├── followers_1.json      (may be followers_1, _2, ... for big accounts)
            └── following.json
```

`exports/` is gitignored, so your data is never committed.

## 3. Run it

```bash
python3 clean_up.py                      # uses the newest DD-MM-YY folder
python3 clean_up.py exports/27-10-26     # or pick one
```

Output:

```text
Following 1338, followers 1319, not following back 184
Wrote exports/27-10-26/unfollow.json
```

## 4. Read the result

`exports/<date>/unfollow.json`:

```json
{
  "generated_at": "2026-10-27T14:30:00+00:00",
  "source": "local Instagram export",
  "source_dir": "27-10-26",
  "snapshot_note": "Snapshot of the export date; may be stale.",
  "counts": { "following": 1338, "followers": 1319, "not_following_back": 184 },
  "accounts": [
    { "username": "example_user", "profile_url": "https://www.instagram.com/_u/example_user" }
  ],
  "warnings": []
}
```

Any `warnings` (malformed records, empty lists) mean the export may be incomplete — re-download it.

## Things to know

- **It's a snapshot.** Anyone who followed you after the export date will still be listed. Download a fresh export for fresh results.
- **Dead links aren't necessarily non-followers.** If a `profile_url` shows "Sorry, this page isn't available", the account was deactivated, deleted, renamed after the export, or has blocked you — the export can't tell which. Renamed accounts can be found by searching your Following list in the app.
- **Unfollowing is up to you**, by hand in the app. Mass-unfollowing quickly can trigger Instagram's action limits.
- **The result is personal data.** Don't share or upload `unfollow.json` casually.

## Tests

```bash
python3 -m unittest -v
```
