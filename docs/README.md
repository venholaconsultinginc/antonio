# Getting started with antonio

*Skeleton — this is the planned entry point for antonio's customer-facing documentation, not the
finished thing. Fill in as Phase 3 report scripts land; see each sport page for what's still a
placeholder.*

`antonio` shows how to query a Cordelia SQLite database and produce basic reports, in Python. New
to Python or don't have dependencies installed yet? Start with [setup](setup.md). Don't have a
database to work with yet? See [how to get one](obtaining-data.md). Otherwise, pick the sport
closest to your own data to see it worked through end to end:

| Sport | Example database | Guide |
|---|---|---|
| Running | [`cordelia-sample-running.sqlite`](downloads.md) | [Guide](running.md) |
| Cycling | [`cordelia-sample-cycling.sqlite`](downloads.md) | [Guide](cycling.md) |
| Kayaking | [`cordelia-sample-kayaking.sqlite`](downloads.md) | [Guide](kayaking.md) |
| Strength training | [`cordelia-sample-strength-training.sqlite`](downloads.md) | [Guide](strength-training.md) |
| Swimming | [`cordelia-sample-swimming.sqlite`](downloads.md) | [Guide](swimming.md) |

Or see [all six databases at a glance](example-databases.md), empty one included.

Already have your own Cordelia database? The same report scripts should work against it directly
— nothing in `antonio` depends on the example data specifically, it's just there so you have
something to run against before you have your own.

All six example databases are fabricated — see [the downloads page](downloads.md) for what that
means, how to verify them, and where to download each one.

For more on Cordelia itself — what it is, how it works, the database it produces — see
[venholaconsulting.ca/apps/help/](https://venholaconsulting.ca/apps/help/). Curious where the name
"antonio" comes from? Read [the story behind it](namesake.md).

## What's still missing

- The report/plotting scripts themselves (Phase 3 — running is done, see the
  [running guide](running.md); cycling/kayaking/strength training/swimming still to come, see
  each sport page above for what they'll show once they exist).
- Troubleshooting section.
