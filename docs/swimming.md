# Swimming

*Skeleton page — placeholder for the swimming getting-started guide, not the finished thing. See
"Still to do" below for what's missing.*

New to Python, or don't have dependencies installed yet? See [setup.md](setup.md) first.

## Example database

26 sessions, one per day through August 2026 (Sundays off), 25&nbsp;m indoor pool, freestyle,
fabricated (no real person, device, or activity represented). Download
`cordelia-sample-swimming.sqlite`, with its SHA-256 checksum and GPG signature, from
[downloads.md](downloads.md).

```bash
sqlite3 example-data/cordelia-sample-swimming.sqlite
```

## What a swimming activity looks like in Cordelia

*TODO: short tour of the tables a swimming activity populates — no GPS, but a `Length` table (one
row per pool length) that doesn't appear for any other sport in this repo.*

## Example reports

*Not written yet — Phase 3. "Route map" doesn't apply here — needs its own report idea (e.g. pace
per 100&nbsp;m across lengths, or session count/distance over the month).*

## Using your own data

*TODO: how to point whichever report script exists at your own Cordelia database instead of the
example one.*

## Still to do

- An `antonio-swimming.png` hero illustration (every other sport page has one).
- Everything else above marked TODO.
