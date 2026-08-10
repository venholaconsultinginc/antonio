# Getting started with antonio

*Skeleton — this is the planned entry point for antonio's customer-facing documentation, not the
finished thing. Fill in as Phase 3 report scripts land; see each sport page for what's still a
placeholder.*

`antonio` shows how to query a Cordelia SQLite database and produce basic reports, in Python. New
to Python or don't have dependencies installed yet? Start with [setup](setup.md). Don't have a
database to work with yet? See [how to get one](obtaining-data.md). Otherwise, pick the sport
closest to your own data to see it worked through end to end:

- [<img src="icon-running.svg" width="32" alt=""> Running](running.md)
- [<img src="icon-cycling.svg" width="32" alt=""> Cycling](cycling.md)
- [<img src="icon-kayaking.svg" width="32" alt=""> Kayaking](kayaking.md)
- [<img src="icon-strength-training.svg" width="32" alt=""> Strength training](strength-training.md)
- [<img src="icon-swimming.svg" width="32" alt=""> Swimming](swimming.md)

Or see [all six databases at a glance](example-databases.md) — including the empty one, plus how
to verify each download.

Already have your own Cordelia database? The same report scripts should work against it directly
— nothing in `antonio` depends on the example data specifically, it's just there so you have
something to run against before you have your own. All six example databases are entirely
fabricated — no real person, device, or activity is represented in any of them.

For more on Cordelia itself — what it is, how it works, the database it produces — see
[venholaconsulting.ca/apps/help/](https://venholaconsulting.ca/apps/help/). Curious where the name
"antonio" comes from? Read [the story behind it](namesake.md).

## What's still missing

- The report/plotting scripts themselves (Phase 3 — running is done, see the
  [running guide](running.md); cycling is too, see the [cycling guide](cycling.md);
  kayaking/strength training/swimming still to come, see
  each sport page above for what they'll show once they exist).
- Troubleshooting section.
