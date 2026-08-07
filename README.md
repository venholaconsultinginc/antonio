# antonio

Read a Cordelia SQLite database, get real plots and summary metrics out of it — in Python you can
read, copy, and make your own.

`antonio` is the "seed" layer for Cordelia's SQLite output: small, readable report scripts plus
documentation walking through them, for anyone who knows Python and wants to start analyzing their
own Garmin activity data (or try it out on realistic fabricated data first). It's not a library
you install and depend on, not a framework — copy what's useful and go make it your own. See
[`docs/namesake.md`](docs/namesake.md) for where the name comes from. For more on Cordelia itself,
the app that produces the databases these scripts read, see
[venholaconsulting.ca/apps/help/](https://venholaconsulting.ca/apps/help/).

## Python scripts to analyze and plot Garmin data in a Cordelia SQLite database

> [!TIP]
> **New here? Start at [`docs/getting-started.md`](docs/getting-started.md)** — pick the sport
> closest to your own activity data and see a working example end to end.

Each script reads a Cordelia database for one sport, prints a few basic summary metrics (total
distance, average pace, heart rate, and the like), and writes a couple of simple plots (trend
lines, route maps) — meant to be read and adapted for your own analysis, not run as-is forever.
Running's script is done; cycling, kayaking, and strength training are still coming.

Don't have a Cordelia database of your own yet? Four ready-to-download example databases (one per
sport, entirely fabricated) are available — see [`docs/downloads.md`](docs/downloads.md).

## Setup

See [`docs/setup.md`](docs/setup.md) for installing Python dependencies and checking your setup
works.

## Repository layout

| Path | Contents |
|---|---|
| `example-data/` | The four pre-built example databases, their checksums/signatures, and the public signing key — see [`docs/downloads.md`](docs/downloads.md). |
| `docs/` | Customer-facing documentation — start at [`docs/getting-started.md`](docs/getting-started.md). |
| `reports/` | The report/plotting scripts, one per sport (in progress — running done, cycling/kayaking/strength training still to come). |
| `requirements.txt` | Python dependencies for the report scripts — see [`docs/setup.md`](docs/setup.md). |
