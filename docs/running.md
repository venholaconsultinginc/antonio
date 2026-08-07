<img src="antonio-running.png" alt="" width="220" align="right">

# Running

## Example database

[`cordelia-sample-running.sqlite`](../example-data/cordelia-sample-running.sqlite) — 30
consecutive daily ~5&nbsp;km runs along a real public route, fabricated (no real person, device,
or activity represented). SHA-256 checksum and GPG signature ship alongside it; see the root
[README](../README.md#example-databases) for how to verify them.

```bash
sqlite3 example-data/cordelia-sample-running.sqlite
```

## Example reports

[`reports/running_report.py`](../reports/running_report.py) reads the example database above and
produces a couple of basic reports — read it and copy from it as a starting point for your own.

Summary metrics printed to stdout:

```
Runs:                30
Total distance:      150.8 km
Total time:          14.6 h
Average pace:        5.80 min/km
Best (fastest) pace: 5.20 min/km
Average heart rate:  145 bpm
```

A pace trend across all 30 runs:

![Pace trend across 30 runs](running-pace-trend.png)

Average heart rate in five-minute buckets of elapsed time, across all 30 runs:

![Average heart rate by five-minute bucket into the run](running-heart-rate-by-bucket.png)

And a GPS route map for the first run:

![GPS route map for one run](running-route-map.png)

Run it yourself:

```bash
python3 reports/running_report.py
```

## Using your own data

The same script works against any Cordelia database, not just the bundled example — pass its path
with `--db`:

```bash
python3 reports/running_report.py --db path/to/your.sqlite
```

By default, plots are written to `reports/output/running/`; pass `--out-dir` to write them
somewhere else.

## What a running activity looks like in Cordelia

The `Record` table, viewed in Cordelia, for one run:

![Cordelia's Tables view, showing the Record table for a running activity](cordelia-screenshot-running-record-table.png)
