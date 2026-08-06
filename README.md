# antonio

Examples of how to generate reports using Python for a Cordelia database.

`antonio` is the "seed" layer for Cordelia's SQLite output: synthetic sample datasets plus (soon)
a handful of basic report scripts, meant to be read and copied, not a maintained tool. See
[`docs/objectives-and-requirements.md`](docs/objectives-and-requirements.md) for what this repo is
and isn't, and [`docs/plan.md`](docs/plan.md) for the phased scope of work and the schema/encoding
detail behind it.

**Status:** two synthetic data generators (Phase 2, running and cycling) are done. The
report/plotting scripts (Phase 3) are not written yet.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Both generators need nothing beyond the standard library; `requirements.txt` covers the report
scripts that will use their output.

## Generating the sample databases

Neither generator writes to a database directly -- each emits plain SQL `INSERT` statements to a
text file, which you then load into a fresh SQLite database of your own. Each generator's
`file_number`s independently start at 1, so **loading both into the same database collides** on
`FileID`'s primary key -- give each its own database:

```bash
python3 generate_sample_data.py                  # writes output/sample_data.sql (running)
python3 generate_sample_data_bike.py              # writes output/sample_data_bike.sql (cycling)

sqlite3 running.sqlite < sql/create_tables.sql
sqlite3 running.sqlite < output/sample_data.sql   # 30 synthetic daily runs

sqlite3 cycling.sqlite < sql/create_tables.sql
sqlite3 cycling.sqlite < output/sample_data_bike.sql  # 4 synthetic rides
```

`generate_sample_data.py` produces 30 consecutive days of one ~5 km run each, along a real public
route (see [`data/SOURCES.md`](data/SOURCES.md)), with +/-10% random variation in pace, heart
rate, cadence, and temperature, and a start time of approximately 9am (+/-10%). See
`generate_sample_data.py --help` for the `--days`, `--start-date`, `--seed`, `--route`, and
`--output` options.

`generate_sample_data_bike.py` produces 4 rides (2026-09-05/12/18/26) of the real ~77 km Tour de
Victoria road-cycling route, starting ~9am (+/-10%), with +/-10% variation in pace/heart
rate/temperature off baselines taken from a real reference ride (not invented, unlike the running
generator's baselines) -- see `docs/plan.md`. Device model codes (Garmin Edge 1040 + a paired Venu
4 for heart rate) are real; serial numbers are fabricated. See `generate_sample_data_bike.py
--help` for the `--dates`, `--seed`, `--route`, and `--output` options.

Everything either generator produces is fabricated -- no real person, device unit, or activity is
represented.

## Repository layout

| Path | Contents |
|---|---|
| `sql/create_tables.sql` | The nine Cordelia tables these generators touch, extracted from the `cordelia` source. |
| `cordelia_db.py` | Shared schema/encoding helpers (semicircle GPS, ISO 8601 timestamps, SQL statement building). |
| `generate_sample_data.py` | The running data generator. |
| `generate_sample_data_bike.py` | The cycling data generator (imports `Route`/`load_route` from the running generator). |
| `data/route_running.gpx` | A real public 5K route used as the running loop; see `data/SOURCES.md` for provenance. |
| `data/route_bike.gpx` | A real public 80 km road-cycling route (Tour de Victoria); see `data/SOURCES.md`. |
| `docs/` | Objectives, requirements, and the full phased plan. |

## Data hygiene

Only ever commit synthetic data produced by these generators. Never commit a real Cordelia export
or any file containing real personal fitness data -- see `CLAUDE.md`.
