# Example databases at a glance

Six pre-built, fabricated Cordelia databases — one per sport, plus a schema-only empty one — ship
in [`example-data/`](../example-data/). No Garmin device, no Cordelia install, and no data of your
own required just to get started. See [downloads.md](downloads.md) for checksums, GPG signatures,
and verification steps.

| | Sport | Contents | File |
|---|---|---|---|
| <img src="icon-running.svg" width="40" alt=""> | Running | 30 consecutive daily ~5&nbsp;km runs along a real public route | [`cordelia-sample-running.sqlite`](../example-data/cordelia-sample-running.sqlite) |
| <img src="icon-cycling.svg" width="40" alt=""> | Cycling | 4 rides along the real Tour de Victoria 80&nbsp;km road-cycling route | [`cordelia-sample-cycling.sqlite`](../example-data/cordelia-sample-cycling.sqlite) |
| <img src="icon-kayaking.svg" width="40" alt=""> | Kayaking | 8 out-and-back paddles in the Gulf Islands | [`cordelia-sample-kayaking.sqlite`](../example-data/cordelia-sample-kayaking.sqlite) |
| <img src="icon-strength-training.svg" width="40" alt=""> | Strength training | 8 sessions of work sets and rest periods — no GPS, no distance or speed | [`cordelia-sample-strength-training.sqlite`](../example-data/cordelia-sample-strength-training.sqlite) |
| <img src="icon-swimming.svg" width="40" alt=""> | Swimming | 26 sessions, one per day through August 2026 (Sundays off), 25&nbsp;m indoor pool, freestyle | [`cordelia-sample-swimming.sqlite`](../example-data/cordelia-sample-swimming.sqlite) |
| <img src="icon-empty.svg" width="40" alt=""> | Empty | Full schema, zero rows — a blank starting point | [`cordelia-sample-empty.sqlite`](../example-data/cordelia-sample-empty.sqlite) |

Each is entirely fabricated — no real person, device, or activity is represented in any of them.
Pick the sport closest to your own activity data (or the empty one, to explore the schema itself)
and see [getting-started.md](getting-started.md) for a walkthrough of each.
