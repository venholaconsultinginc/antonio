<img src="antonio-kayaking.png" alt="" width="220" align="right">

# Kayaking

New to Python, or don't have dependencies installed yet? See [setup](setup.md) first.

## Example database

8 out-and-back paddles; fabricated (no real person, device or activity represented). Download
`cordelia-sample-kayaking.sqlite`, with its SHA-256 checksum and GPG signature, from
[the downloads page](example-databases.md).

```bash
sqlite3 example-data/cordelia-sample-kayaking.sqlite
```

![Map of the Gulf Islands kayaking route used for the kayaking example data](gulf-islands-kayaking.png)

## What a kayaking activity looks like in Cordelia

In `Record`, the `Speed` column reads `0` all the way down, the same legacy-field quirk cycling
hits; the report script sidesteps it by deriving pace from `total_distance`/`total_timer_time`
rather than a speed field. Cordelia's schema also has no wind field anywhere, and wind is one of
the biggest swings on paddling pace.

Here is the `Record` table, viewed in Cordelia, for one paddle:

![Cordelia's Tables view, showing the Record table for a kayaking activity](cordelia-screenshot-kayaking-record-table.png)

## Example reports

[`reports/kayaking_report.py`](../reports/kayaking_report.py) reads the example database above and
produces a couple of basic reports. Read it and copy from it as a starting point for your own.

Summary metrics printed to stdout:

```
Paddles:             8
Total distance:      45.7 km
Total time:          12.2 h
Average pace:        16.02 min/km
Best (fastest) pace: 14.64 min/km
Average stroke rate: 22 strokes/min
Average heart rate:  119 bpm
```

A pace trend across all 8 paddles:

![Pace trend across 8 paddles](kayaking-pace-trend.png)

Average heart rate in five-minute buckets of elapsed time, across all 8 paddles:

![Average heart rate by five-minute bucket into the paddle](kayaking-heart-rate-by-bucket.png)

And a GPS route map for the first paddle:

![GPS route map for one paddle](kayaking-route-map.png)

Run it yourself:

```bash
python3 reports/kayaking_report.py
```

## Using your own data

The script works against any Cordelia database. Pass the path with `--db`:

```bash
python3 reports/kayaking_report.py --db path/to/your.sqlite
```

Plots go to `reports/output/kayaking/` by default; pass `--out-dir` to write them somewhere else.

---

**More guides:** [Running](running.md) · [Cycling](cycling.md) · [Strength training](strength-training.md) · [Swimming](swimming.md). Or back to [Getting started](README.md).
