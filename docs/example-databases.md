# Example databases at a glance

Six pre-built, fabricated Cordelia databases — one per sport, plus a schema-only empty one — ship
in [`example-data/`](../example-data/). No Garmin device, no Cordelia install, and no data of your
own required just to get started. See [the downloads page](downloads.md) for checksums, GPG
signatures, and verification steps.

| | Sport | Contents | File |
|---|---|---|---|
| <img src="icon-running.svg" width="56" alt=""> | Running | 30 consecutive daily ~5&nbsp;km runs along a real public route<br>Aug 1–30, 2026 · Ottawa River Pathway, Ottawa ON<br>Avg 29.2 min · 5.8 min/km pace | [`cordelia-sample-running.sqlite`](../example-data/cordelia-sample-running.sqlite) |
| <img src="icon-cycling.svg" width="56" alt=""> | Cycling | 4 rides along the real Tour de Victoria 80&nbsp;km road-cycling route<br>Sep 5–26, 2026 · Victoria, BC<br>Avg 204.5 min (~3h25m) · 22.6 km/h avg speed | [`cordelia-sample-cycling.sqlite`](../example-data/cordelia-sample-cycling.sqlite) |
| <img src="icon-kayaking.svg" width="56" alt=""> | Kayaking | 8 out-and-back paddles in the Gulf Islands<br>Sep 4–27, 2026 · Mayne Island, BC<br>Avg 91.6 min (~1h32m) · 45.7&nbsp;km total (~5.7&nbsp;km/paddle) | [`cordelia-sample-kayaking.sqlite`](../example-data/cordelia-sample-kayaking.sqlite) |
| <img src="icon-strength-training.svg" width="56" alt=""> | Strength training | 8 sessions of work sets and rest periods — no GPS, no distance or speed<br>Sep 1–24, 2026 · indoor (no GPS)<br>Avg 51.3 min · 51 work sets + 50 rest periods/session | [`cordelia-sample-strength-training.sqlite`](../example-data/cordelia-sample-strength-training.sqlite) |
| <img src="icon-swimming.svg" width="56" alt=""> | Swimming | 26 sessions, one per day through August 2026 (Sundays off), 25&nbsp;m indoor pool, freestyle<br>Aug 1–31, 2026 · indoor pool (no GPS)<br>Avg 20.9 min · 41 lengths/session | [`cordelia-sample-swimming.sqlite`](../example-data/cordelia-sample-swimming.sqlite) |
| <img src="icon-empty.svg" width="56" alt=""> | Empty | Full schema, zero rows — a blank starting point<br>127 tables (Cordelia's full schema) | [`cordelia-sample-empty.sqlite`](../example-data/cordelia-sample-empty.sqlite) |

Each is entirely fabricated — no real person, device, or activity is represented in any of them.
Pick the sport closest to your own activity data (or the empty one, to explore the schema itself)
and see [Getting started](README.md) for a walkthrough of each.
