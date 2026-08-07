# Getting started with antonio

*Skeleton — this is the planned entry point for antonio's customer-facing documentation, not the
finished thing. Fill in as Phase 3 report scripts land; see each sport page for what's still a
placeholder.*

`antonio` shows how to query a Cordelia SQLite database and produce basic reports, in Python. Don't
have a database to work with yet? See [obtaining-data.md](obtaining-data.md) first. Otherwise, pick
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

All four example databases are fabricated — see the root [README](../README.md#example-databases)
for what that means and how to verify them.

For more on Cordelia itself — what it is, how it works, the database it produces — see
[venholaconsulting.ca/apps/help/](https://venholaconsulting.ca/apps/help/). Curious where the name
"antonio" comes from? See [namesake.md](namesake.md).

## What's still missing

- The report/plotting scripts themselves (Phase 3 — running is done, see
  [running.md](running.md); cycling/kayaking/strength training still to come, see each sport page
  below for what they'll show once they exist).
- Install/setup walkthrough beyond the root README's `pip install -r requirements.txt`.
- Troubleshooting section.
