# antonio

Examples of how to generate reports using Python for a Cordelia database.

`antonio` is the "seed" layer for Cordelia's SQLite output: a synthetic sample dataset plus (soon)
a handful of basic report scripts, meant to be read and copied, not a maintained tool. See
[`docs/objectives-and-requirements.md`](docs/objectives-and-requirements.md) for what this repo is
and isn't, and [`docs/plan.md`](docs/plan.md) for the phased scope of work and the schema/encoding
detail behind it.

**Status:** the synthetic data generator (Phase 2) is done. The report/plotting scripts
(Phase 3) are not written yet.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`generate_sample_data.py` itself needs nothing beyond the standard library; `requirements.txt`
covers the report scripts that will use it.

## Generating the sample database

`generate_sample_data.py` does not write to a database directly -- it emits plain SQL `INSERT`
statements to a text file, which you then load into a fresh SQLite database of your own:

```bash
python3 generate_sample_data.py                 # writes output/sample_data.sql

sqlite3 mydb.sqlite < sql/create_tables.sql      # create the Cordelia-schema subset
sqlite3 mydb.sqlite < output/sample_data.sql     # load the 30 synthetic daily runs
```

This produces 30 consecutive days of one ~5 km run each, along a real public route (see
[`data/SOURCES.md`](data/SOURCES.md)), with +/-10% random variation in pace, heart rate, cadence,
and temperature, and a start time of approximately 9am (+/-10%). Everything is fabricated --
no real person, device, or activity is represented. See `generate_sample_data.py --help` for the
`--days`, `--start-date`, `--seed`, `--route`, and `--output` options.

## Repository layout

| Path | Contents |
|---|---|
| `sql/create_tables.sql` | The seven Cordelia tables this repo touches, extracted from the `cordelia` source. |
| `cordelia_db.py` | Shared schema/encoding helpers (semicircle GPS, Garmin-epoch time, ISO 8601 timestamps, SQL statement building). |
| `generate_sample_data.py` | The synthetic data generator. |
| `data/route.gpx` | A real public 5K route used as the run loop; see `data/SOURCES.md` for provenance. |
| `docs/` | Objectives, requirements, and the full phased plan. |

## Data hygiene

Only ever commit synthetic data produced by `generate_sample_data.py`. Never commit a real
Cordelia export or any file containing real personal fitness data -- see `CLAUDE.md`.
