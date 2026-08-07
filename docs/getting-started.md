# Getting started with antonio

*Skeleton — this is the planned entry point for antonio's customer-facing documentation, not the
finished thing. Fill in as Phase 3 report scripts land; see each sport page for what's still a
placeholder.*

`antonio` shows how to query a Cordelia SQLite database and produce basic reports, in Python. Pick
the sport closest to your own data to see it worked through end to end:

| Sport | Example database | Guide |
|---|---|---|
| Running | [`cordelia-sample-running.sqlite`](../example-data/cordelia-sample-running.sqlite) | [running.md](running.md) |
| Cycling | [`cordelia-sample-cycling.sqlite`](../example-data/cordelia-sample-cycling.sqlite) | [cycling.md](cycling.md) |
| Kayaking | [`cordelia-sample-kayaking.sqlite`](../example-data/cordelia-sample-kayaking.sqlite) | [kayaking.md](kayaking.md) |
| Strength training | [`cordelia-sample-strength-training.sqlite`](../example-data/cordelia-sample-strength-training.sqlite) | [strength-training.md](strength-training.md) |

Already have your own Cordelia database? The same report scripts should work against it directly
— nothing in `antonio` depends on the example data specifically, it's just there so you have
something to run against before you have your own.

All four example databases are fabricated (see the root [README](../README.md#example-databases)
for what that means and how to verify them) and built by a separate, private repo,
[`data_generators`](https://github.com/venholaconsultinginc/data_generators) — not something you
need to touch to use antonio itself.

## What's still missing

- The report/plotting scripts themselves (Phase 3 — see each sport page below for what it'll
  show once they exist).
- Install/setup walkthrough beyond the root README's `pip install -r requirements.txt`.
- Troubleshooting section.
