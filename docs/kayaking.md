<img src="antonio-kayaking.png" alt="" width="220" align="right">

# Kayaking

*Skeleton page — placeholder for the kayaking getting-started guide, not the finished thing. See
"Still to do" below for what's missing.*

New to Python, or don't have dependencies installed yet? See [setup](setup.md) first.

## Example database

8 out-and-back paddles, fabricated (no real person, device, or activity represented). Download
`cordelia-sample-kayaking.sqlite`, with its SHA-256 checksum and GPG signature, from
[the downloads page](example-databases.md).

```bash
sqlite3 example-data/cordelia-sample-kayaking.sqlite
```

![Map of the Gulf Islands kayaking route used for the kayaking example data](gulf-islands-kayaking.png)

## What a kayaking activity looks like in Cordelia

*TODO: short tour of the tables a kayaking activity populates (same set as cycling) and the
wind-as-a-pace-effect detail worth calling out (no wind field exists anywhere in Cordelia's
schema) — plus a Cordelia screenshot, matching running.md's.*

## Example reports

[`reports/kayaking_report.py`](../reports/kayaking_report.py) reads the example database above and
produces a couple of basic reports — read it and copy from it as a starting point for your own.

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

The same script works against any Cordelia database, not just the bundled example — pass its path
with `--db`:

```bash
python3 reports/kayaking_report.py --db path/to/your.sqlite
```

By default, plots are written to `reports/output/kayaking/`; pass `--out-dir` to write them
somewhere else.

## Still to do

- The Cordelia-schema tour and screenshot noted above.

---

**More guides:** [Running](running.md) · [Cycling](cycling.md) · [Strength training](strength-training.md) · [Swimming](swimming.md) — or back to [Getting started](README.md).
