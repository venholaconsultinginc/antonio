<img src="antonio-strength-training.png" alt="" width="220" align="right">

# Strength training

New to Python, or don't have dependencies installed yet? See [setup](setup.md) first.

## Example database

8 sessions of 51 work sets and 50 rest periods each; fabricated (no real person, device or activity
represented). Download `cordelia-sample-strength-training.sqlite`, with its SHA-256 checksum and
GPG signature, from [the downloads page](example-databases.md).

```bash
sqlite3 example-data/cordelia-sample-strength-training.sqlite
```

## What a strength-training activity looks like in Cordelia

A genuinely different shape from every other sport here: no GPS, no `Distance`, no `Speed`. In
their place is a `SetX` table, one row per work set or rest period, carrying `Repetitions`,
`Weight`, `Duration` and FIT's own exercise-category codes. `Session` and `Lap` summaries are as
usual; `Record` holds heart rate and nothing else.

## Example reports

[`reports/strength_training_report.py`](../reports/strength_training_report.py) reads the example
database above and produces a few basic reports. Read it and copy from it as a starting point for
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
Distinct exercises:  20
Biggest exercise:    Lat Pulldown (15,750 kg)
```

And the routine itself. Every session replays the same one, so these are exact counts rather than
averages, listed in the order performed. The last five are single-set stretching and mobility work,
so they get a table of their own. The commentary is Antonio's; he is a sea captain by trade, so his
frame of reference is what it is.

**The main circuit**, 46 of the 51 work sets:

| | Exercise | Sets | Reps | Weight | Antonio says |
|:---:|:---|---:|---:|---:|:---|
| <img src="exercises/weighted-crunch.svg" width="84" alt=""> | Weighted Crunch | 3 | 8–11 | 15–20 kg | For the abs. Cordelia is in an entirely different play, but a man can hope. |
| <img src="exercises/curl.svg" width="59" alt=""> | Curl † | 3 | 10–11 | 40–45 kg |  |
| <img src="exercises/shrug.svg" width="60" alt=""> | Shrug † | 3 | 8–11 | 15–20 kg | Also my answer when anyone asks where my purse went. |
| <img src="exercises/overhead-barbell-press.svg" width="58" alt=""> | Overhead Barbell Press | 3 | 10 | 15–20 kg |  |
| <img src="exercises/chest-supported-dumbbell-row.svg" width="84" alt=""> | Chest Supported Dumbbell Row | 3 | 9–11 | 40–45 kg | I captain a ship and paddle a kayak. Rowing, at least, I have references for. |
| <img src="exercises/weighted-leg-extensions.svg" width="77" alt=""> | Weighted Leg Extensions | 3 | 10 | 20–25 kg | Eighty kilometres of the Victoria route says these are earning their keep. |
| <img src="exercises/seated-cable-row.svg" width="84" alt=""> | Seated Cable Row | 3 | 10–11 | 50–55 kg | Rowing that goes nowhere. The sea never charged me a membership. |
| <img src="exercises/lat-pulldown.svg" width="54" alt=""> | Lat Pulldown | 3 | 11–12 | 55–60 kg | Hauling rope by another name. The rigging taught me this one for free. |
| <img src="exercises/elbow-to-knee-crunch.svg" width="84" alt=""> | Elbow To Knee Crunch | 3 | 10 | None recorded |  |
| <img src="exercises/weighted-balancing-squat.svg" width="73" alt=""> | Weighted Balancing Squat | 3 | 9 | 20–25 kg | Balancing on a floor that refuses to pitch. Frankly, it feels like cheating. |
| <img src="exercises/stretch-lying-it-band.svg" width="84" alt=""> | Stretch Lying It Band | 3 | 9–11 | 10–15 kg |  |
| <img src="exercises/glute-bridge.svg" width="84" alt=""> | Glute Bridge | 3 | 6–11 | 25–30 kg |  |
| <img src="exercises/chin-up.svg" width="31" alt=""> | Chin Up | 3 | 9–10 | None recorded | Hardest of the lot. I once hauled a whole man out of the sea; now I manage nine. |
| <img src="exercises/push-up.svg" width="84" alt=""> | Push Up † | 4 | 6–10 | None recorded | I should push myself harder here. Four sets is barely a squall. |
| <img src="exercises/weighted-standing-hip-abduction.svg" width="60" alt=""> | Weighted Standing Hip Abduction | 3 | 6–9 | 40–45 kg |  |
| | **Total** | **46** | | | |

**Cool-down**, the remaining 5, one set each:

| | Exercise | Sets | Reps | Weight | Antonio says |
|:---:|:---|---:|---:|---:|:---|
| <img src="exercises/stretch-shoulder.svg" width="60" alt=""> | Stretch Shoulder | 1 | 1 | None recorded | Twenty-six mornings of freestyle in a 25-metre pool. The shoulders remember. |
| <img src="exercises/hamstring-stretch.svg" width="84" alt=""> | Hamstring Stretch | 1 | 1 | None recorded | Twenty-five runs in August, not one stretch among them. This is the invoice. |
| <img src="exercises/stretch-side.svg" width="68" alt=""> | Stretch Side | 1 | 2 | None recorded |  |
| <img src="exercises/groiners.svg" width="84" alt=""> | Groiners | 1 | 1 | None recorded | My right knee lodges a formal complaint every single time. |
| <img src="exercises/stretch-forearms.svg" width="61" alt=""> | Stretch Forearms | 1 | 2 | None recorded | Rope, oar, purse. They have earned it. |
| | **Total** | **5** | | | |

† Carries a category code but no more specific subtype, so it reads as the broad movement rather
than a named variant: the `COALESCE` fallback described below, visible in the data.

**"None recorded"** means weight 0, which covers two things the FIT file can't tell apart:
genuine bodyweight work (the chin-ups, push-ups and crunches) and the cool-down, which Garmin
Connect displays as "--" rather than "Bodyweight". Where a weight *is* recorded it reads as a
range, because the last two sessions add 5 kg to every already-weighted set. That
progressive-overload step shows up in the progression plot below.

The script prints the same breakdown to stdout, so it follows whatever database you point it at.

Volume, meaning reps × weight, totalled for each workout:

![Volume lifted per workout across the eight example sessions](strength-training-volume-per-workout.png)

The exercises that contributed the most of that volume:

![The eight exercises contributing the most volume](strength-training-top-exercises.png)

And progression for the biggest one by volume, the heaviest set recorded in each workout:

![Heaviest set per workout for the lat pulldown](strength-training-progression.png)

Run it yourself:

```bash
python3 reports/strength_training_report.py
```

### Where the exercise names come from

A `SetX` row doesn't store "Seated Cable Row". It stores two Garmin codes: a category
(`raw_category_garmin_key`, e.g. `23`) and a more specific subtype
(`raw_category_subtype_garmin_key`, e.g. `23 18`). Cordelia's `better_labels_definitions` and
`better_labels_lookup` tables turn those into readable text, and the script joins them with a
`COALESCE` that prefers the subtype ("Seated Cable Row"), falls back to the category ("Row"), and
falls back again to "Unspecified" when a set carries neither code.

Every set in this example database carries a code, so nothing lands in that last bucket here. Your
own data probably will: a watch counts reps whether or not anyone told it what movement was
performed, and a set logged without an exercise selected has nothing to name it. Those sets are
real work and stay in the totals; they just can't be charted or listed per exercise. The summary
prints a "Sets with no exercise recorded" line whenever there are any.

The middle branch of that `COALESCE` is the one marked † in the circuit table above: **Curl**,
**Shrug** and **Push Up**. Everything else in the example resolves to a specific named variant.

Those labels exist in six locales, though that mostly buys you the *category* names; Garmin's
per-exercise subtype names are largely untranslated in the source data. Of the twenty exercises
above, only two change in French, both of them category-level, and French keeps "Curl" as it is:

```bash
python3 reports/strength_training_report.py --locale fr
# Shrug   ->  Haussement d'épaules
# Push Up ->  Pompe
```

## Using your own data

The script works against any Cordelia database. Pass the path with `--db`:

```bash
python3 reports/strength_training_report.py --db path/to/your.sqlite
```

Plots go to `reports/output/strength-training/` by default; pass `--out-dir` to write them
somewhere else.

Before you read too much into your own numbers: edits you make in Garmin Connect after a workout
stay there and never reach the FIT file. That covers a set's weight, so `SetX.Weight` is whatever
the watch recorded at the time, and it covers the **exercise name** just as much. Correct an
exercise in Connect after the session and the file still holds whatever the watch guessed, which is
what these reports will name. Connect showing one thing and this script another is expected rather
than a bug in either.

---

**More guides:** [Running](running.md) · [Cycling](cycling.md) · [Kayaking](kayaking.md) · [Swimming](swimming.md). Or back to [Getting started](README.md).
