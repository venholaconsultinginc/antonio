<img src="antonio-strength-training.png" alt="" width="220" align="right">

# Strength training

*The report script and its examples below are real. The tour of `SetX`'s columns is still to be
written — see the TODO in "What a strength-training activity looks like in Cordelia".*

New to Python, or don't have dependencies installed yet? See [setup](setup.md) first.

## Example database

8 sessions (51 work sets, 50 rest periods each), fabricated (no real person, device, or activity
represented). Download `cordelia-sample-strength-training.sqlite`, with its SHA-256 checksum and
GPG signature, from [the downloads page](example-databases.md).

```bash
sqlite3 example-data/cordelia-sample-strength-training.sqlite
```

## What a strength-training activity looks like in Cordelia

Genuinely different shape from the other three sports: no GPS, no `Distance`, no `Speed` — instead
a `SetX` table (one row per work set or rest period, with `Repetitions`, `Weight`, `Duration`, and
FIT's own exercise-category codes) alongside `Session`/`Lap` summaries and a heart-rate-only
`Record` table.

*TODO: short tour of `SetX`'s columns and how they map to what you'd see in Garmin Connect.*

## Example reports

[`reports/strength_training_report.py`](../reports/strength_training_report.py) reads the example
database above and produces a few basic reports — read it and copy from it as a starting point for
your own.

Summary metrics printed to stdout:

```
Workouts:            8
Date range:          2026-09-01 to 2026-09-24
Working sets:        408 (400 rest periods)
Total repetitions:   3632
Total volume:        86,040 kg
Heaviest set:        60 kg
Average workout:     51 min
Average heart rate:  126 bpm
Distinct exercises:  14
Biggest exercise:    Alternating Incline Dumbbell Biceps Curl (11,370 kg)
Sets with no exercise recorded: 160 of 408 (39%) — counted in the totals above, left out of the per-exercise plots
```

Volume — reps × weight — totalled for each workout:

![Volume lifted per workout across the eight example sessions](strength-training-volume-per-workout.png)

The exercises that contributed the most of that volume:

![The eight exercises contributing the most volume](strength-training-top-exercises.png)

And progression for the biggest one, the heaviest set recorded in each workout:

![Heaviest set per workout for the alternating incline dumbbell biceps curl](strength-training-progression.png)

Run it yourself:

```bash
python3 reports/strength_training_report.py
```

### Where the exercise names come from

A `SetX` row doesn't store "Seated Cable Row". It stores two Garmin codes — a category
(`raw_category_garmin_key`, e.g. `23`) and a more specific subtype
(`raw_category_subtype_garmin_key`, e.g. `23 18`) — and Cordelia's `better_labels_definitions` and
`better_labels_lookup` tables turn those into readable text. The script joins them with a
`COALESCE` that prefers the subtype ("Seated Cable Row"), falls back to the category ("Row"), and
falls back again to "Unspecified" when a set carries neither code, which is why 39% of the example
sets land in that last bucket. That's realistic: a watch counts reps whether or not anyone told it
what movement was being performed. Those sets still count toward the totals; they just can't be
charted per exercise.

Those labels exist in six locales, so the same script prints French or German exercise names with
one flag:

```bash
python3 reports/strength_training_report.py --locale fr
```

## Using your own data

The same script works against any Cordelia database, not just the bundled example — pass its path
with `--db`:

```bash
python3 reports/strength_training_report.py --db path/to/your.sqlite
```

By default, plots are written to `reports/output/strength-training/`; pass `--out-dir` to write
them somewhere else.

One thing to know before you read too much into your own numbers: if you edit a set's weight in
Garmin Connect after a workout, that edit stays in Garmin Connect. It never propagates back into
the FIT file, so `SetX.Weight` here is whatever the watch recorded at the time.

---

**More guides:** [Running](running.md) · [Cycling](cycling.md) · [Kayaking](kayaking.md) · [Swimming](swimming.md) — or back to [Getting started](README.md).
