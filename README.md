# antonio

Point a Python script at a Cordelia SQLite database and get plots and summary metrics back out.
The scripts are short enough to read start to finish, and they're meant to be copied and adapted
rather than run as-is forever.

`antonio` is the seed layer for Cordelia's SQLite output: small report scripts, with documentation
walking through each one, for anybody who knows Python and wants to start analyzing their own
Garmin activity data. It isn't a library you install or a framework you build on. The name has
[a story behind it](docs/namesake.md), and Cordelia, the app that writes these databases, is
documented at [venholaconsulting.ca/apps/help/](https://venholaconsulting.ca/apps/help/).

## Python scripts to analyze and plot Garmin data in a Cordelia SQLite database

> [!TIP]
> **New here? Start with [Getting started](docs/README.md).** Pick the sport closest to your own
> activity data and see a working example end to end.

Each script covers one sport, prints a few summary metrics (total distance, average pace, heart
rate and the like) and writes a few plots such as trend lines and route maps. There are five:
running, cycling, kayaking, strength training and swimming.

No Cordelia database of your own yet? Six example databases are ready to download from
[the downloads page](docs/example-databases.md), one per sport plus an empty one, all entirely
fabricated.

## Setup

Installing Python dependencies and checking your setup works: see the [setup guide](docs/setup.md).

## Repository layout

| Path | Contents |
|---|---|
| `example-data/` | The six pre-built example databases, their checksums and signatures, and the public signing key. See [the downloads page](docs/example-databases.md). |
| `docs/` | Customer-facing documentation. Start at [Getting started](docs/README.md). |
| `reports/` | The report and plotting scripts, one per sport. |
| `requirements.txt` | Python dependencies for the report scripts; see the [setup guide](docs/setup.md). |
| `CONTRIBUTING.md` | How to report a bug, ask for a feature, or open a pull request. |
