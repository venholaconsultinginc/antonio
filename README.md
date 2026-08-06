# antonio

Examples of how to generate reports using Python for a Cordelia database.

`antonio` is the "seed" layer for Cordelia's SQLite output: a handful of basic report scripts,
meant to be read and copied, not a maintained tool, plus the getting-started documentation for
them.

**Status:** report/plotting scripts are not written yet. `docs/` already has the illustration
assets prepared for the future per-sport help pages (running, biking, kayaking, strength
training).

Demo data generation lives in a separate, private sibling repo,
[`data_generators`](https://github.com/venholaconsultinginc/data_generators) — moved out of here
on 2026-08-06, since none of that machinery is customer-facing. If you want a demo `.sqlite`
database to develop a report script against, clone that repo separately and run whichever
generator matches the sport you're working on (running, cycling, kayaking, or strength training).

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` (pandas, matplotlib) is a forward declaration for the report scripts — nothing
in this repo needs it yet.

## Repository layout

| Path | Contents |
|---|---|
| `docs/` | Illustration assets for the future per-sport help pages; getting-started documentation once written. |
| `requirements.txt` | Forward declaration for the report scripts (pandas, matplotlib). |

## Data hygiene

This repo never contains real personal fitness data — see `CLAUDE.md`.
