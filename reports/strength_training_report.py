#!/usr/bin/env python3
"""Example visual report for a Cordelia STRENGTH TRAINING database.

Prints a few basic summary metrics and writes three plots: volume lifted per
workout, the exercises contributing the most volume, and weight progression
for the single biggest exercise. Meant as a starting point to read and copy
for your own reports, not a maintained tool — see antonio's README for that
framing.

Strength training has no route to map and no pace to trend, so this report is
built around what a set actually records: reps, weight, and the exercise being
performed. The exercise names come from Cordelia's `better_labels_*` tables,
which translate Garmin's numeric codes into readable text in six locales — see
`load_sets()` for how that join works.

Usage:
    python3 reports/strength_training_report.py
    python3 reports/strength_training_report.py --db path/to/your.sqlite --out-dir out/
    python3 reports/strength_training_report.py --locale fr
"""

import argparse
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DEFAULT_DB = (
    Path(__file__).resolve().parent.parent / "example-data" / "cordelia-sample-strength-training.sqlite"
)

# better_labels_lookup carries every label in these six locales.
LOCALES = ("en", "fr", "es", "de", "it", "ptbr")


def load_sessions(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(
        """
        SELECT file_number, start_time, total_timer_time, total_calories, avg_heart_rate
        FROM Session
        ORDER BY start_time
        """,
        conn,
        parse_dates=["start_time"],
    )


def load_sets(conn: sqlite3.Connection, locale: str = "en") -> pd.DataFrame:
    """Every set, with its exercise name resolved to readable text.

    A SetX row identifies its exercise with two Garmin codes: a category
    (`raw_category_garmin_key`, e.g. "23") and a more specific subtype
    (`raw_category_subtype_garmin_key`, e.g. "23 18"). Both are keys into
    better_labels_definitions under the `setx_category` domain, and
    better_labels_lookup turns a definition into text for one locale.

    Prefer the subtype, which names the actual movement ("Seated Cable Row");
    fall back to the category ("Row") when a watch recorded only that — the
    example database's Curl, Shrug and Push Up sets are exactly that case; fall
    back again to "Unspecified" when it recorded neither, which happens for sets
    logged without an exercise selected.
    """
    return pd.read_sql_query(
        """
        SELECT s.file_number,
               s.Timestamp,
               s.message_index,
               s.Duration          AS duration_s,
               s.Repetitions       AS reps,
               s.Weight            AS weight_kg,
               COALESCE(subtype_label.value, category_label.value, 'Unspecified') AS exercise,
               s.set_type                                                         AS set_type_id,
               COALESCE(set_type_label.value, 'Unknown')                          AS set_type
        FROM SetX s
        LEFT JOIN better_labels_definitions category_def
               ON category_def.domain = 'setx_category'
              AND category_def.garmin_key = s.raw_category_garmin_key
        LEFT JOIN better_labels_lookup category_label
               ON category_label.better_labels_id = category_def.better_labels_id
              AND category_label.locale = :locale
        LEFT JOIN better_labels_definitions subtype_def
               ON subtype_def.domain = 'setx_category'
              AND subtype_def.garmin_key = s.raw_category_subtype_garmin_key
        LEFT JOIN better_labels_lookup subtype_label
               ON subtype_label.better_labels_id = subtype_def.better_labels_id
              AND subtype_label.locale = :locale
        LEFT JOIN better_labels_definitions set_type_def
               ON set_type_def.domain = 'set_type'
              AND set_type_def.garmin_key = CAST(s.set_type AS TEXT)
        LEFT JOIN better_labels_lookup set_type_label
               ON set_type_label.better_labels_id = set_type_def.better_labels_id
              AND set_type_label.locale = :locale
        ORDER BY s.Timestamp, s.message_index
        """,
        conn,
        params={"locale": locale},
        parse_dates=["Timestamp"],
    )


# FIT's own set_type enum: 0 is a rest period, 1 is a work set.
SET_TYPE_ACTIVE = 1


def working_sets(sets: pd.DataFrame) -> pd.DataFrame:
    """Just the sets you lifted in — the rest periods between them are also SetX rows.

    Filters on the raw FIT enum, not on `set_type`'s display text. The text is
    translated like every other better_labels value, so matching it against
    "Active" silently discarded every set under --locale fr ("Actif") or de
    ("Aktiv"), leaving a report of zero working sets.
    """
    return sets[sets["set_type_id"] == SET_TYPE_ACTIVE]


def named_sets(sets: pd.DataFrame) -> pd.DataFrame:
    """Sets whose exercise the watch actually recorded.

    A set can carry no exercise code at all — the watch counted reps, but
    nothing said what movement they were. Those sets are real work and stay in
    the totals, but they can't be charted per exercise, so the per-exercise
    plots and the breakdown table use this subset instead.

    The bundled example database has none of them, so this filter passes
    everything through there. Your own data very likely does have some: it
    happens whenever a set is logged without an exercise selected. The
    "Sets with no exercise recorded" line in the summary tells you how many.
    """
    return sets[sets["exercise"] != "Unspecified"]


def add_volume(sets: pd.DataFrame) -> pd.DataFrame:
    """Volume is the usual reps x weight. Bodyweight and band work records
    weight 0, so those sets count reps but contribute no volume."""
    sets = sets.copy()
    sets["volume_kg"] = sets["reps"] * sets["weight_kg"]
    return sets


def volume_per_session(sets: pd.DataFrame, sessions: pd.DataFrame) -> pd.DataFrame:
    per_file = sets.groupby("file_number")["volume_kg"].sum().rename("volume_kg")
    return sessions.join(per_file, on="file_number")


def print_summary(sessions: pd.DataFrame, sets: pd.DataFrame, all_sets: pd.DataFrame) -> None:
    weighted = sets[sets["weight_kg"] > 0]
    named = named_sets(sets)
    unnamed = len(sets) - len(named)
    by_volume = named.groupby("exercise")["volume_kg"].sum().sort_values(ascending=False)

    print(f"Workouts:            {len(sessions)}")
    print(f"Date range:          {sessions['start_time'].min().date()} to {sessions['start_time'].max().date()}")
    print(f"Working sets:        {len(sets)} ({len(all_sets) - len(sets)} rest periods)")
    print(f"Total repetitions:   {int(sets['reps'].sum())}")
    print(f"Total volume:        {sets['volume_kg'].sum():,.0f} kg")
    print(f"Heaviest set:        {weighted['weight_kg'].max():.0f} kg")
    print(f"Average workout:     {sessions['total_timer_time'].mean() / 60:.0f} min")
    if sessions["avg_heart_rate"].notna().any():
        print(f"Average heart rate:  {sessions['avg_heart_rate'].mean():.0f} bpm")
    print(f"Distinct exercises:  {named['exercise'].nunique()}")
    print(f"Biggest exercise:    {by_volume.index[0]} ({by_volume.iloc[0]:,.0f} kg)")
    if unnamed:
        share = unnamed / len(sets) * 100
        print(
            f"Sets with no exercise recorded: {unnamed} of {len(sets)} ({share:.0f}%)"
            " — counted in the totals above, left out of the per-exercise plots"
        )


def exercise_breakdown(sets: pd.DataFrame, n_workouts: int) -> pd.DataFrame:
    """One row per exercise: how many sets, at what reps, at what weight.

    Ordered by first appearance, so the table reads in the order the workout is
    actually performed. That is deliberately a different question from the
    top-exercises plot's "what moved the most weight" — this one answers "what
    is the routine".

    Order comes from `message_index`, the set's own position in the file, NOT
    from `Timestamp`: a SetX row's Timestamp is the session's timestamp repeated
    on every row of that session, so it is identical for all 101 rows and sorts
    nothing. (`start_time` is the per-set time, if you need a real clock value.)

    Sets are reported per workout rather than as a raw total, since that is the
    figure you'd compare against a training plan. It is a mean: if you did three
    sets of an exercise in one workout and four in another, it reads 3.5.
    """
    named = named_sets(sets)
    grouped = named.groupby("exercise")
    table = pd.DataFrame(
        {
            "first_performed": grouped["message_index"].min(),
            "sets": grouped.size(),
            "reps_low": grouped["reps"].min(),
            "reps_high": grouped["reps"].max(),
            "weight_low": grouped["weight_kg"].min(),
            "weight_high": grouped["weight_kg"].max(),
        }
    ).sort_values("first_performed")
    table["sets_per_workout"] = table["sets"] / n_workouts
    return table


def _range_text(low: float, high: float, suffix: str = "") -> str:
    """"10" for a single value, "10-12" for a range — no false precision either way."""
    if low == high:
        return f"{low:.0f}{suffix}"
    return f"{low:.0f}-{high:.0f}{suffix}"


def print_exercise_breakdown(sets: pd.DataFrame, sessions: pd.DataFrame) -> None:
    table = exercise_breakdown(sets, len(sessions))
    if table.empty:
        return

    name_width = max(len("Exercise"), *(len(name) for name in table.index))
    print()
    print(f"Per exercise, in the order performed, across {len(sessions)} workouts:")
    print()
    print(f"  {'Exercise':<{name_width}}  {'Sets/workout':>12}  {'Reps':>7}  Weight")
    for exercise, row in table.iterrows():
        per_workout = row["sets_per_workout"]
        sets_text = f"{per_workout:.0f}" if float(per_workout).is_integer() else f"{per_workout:.1f}"
        reps_text = _range_text(row["reps_low"], row["reps_high"])
        # Weight 0 covers both genuine bodyweight work and sets a device records
        # without a weight at all; the FIT file doesn't distinguish them, so
        # neither does this.
        if row["weight_high"] == 0:
            weight_text = "none recorded"
        else:
            weight_text = _range_text(row["weight_low"], row["weight_high"], " kg")
        print(f"  {exercise:<{name_width}}  {sets_text:>12}  {reps_text:>7}  {weight_text}")


def plot_volume_per_session(per_session: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(per_session["start_time"].dt.date.astype(str), per_session["volume_kg"])
    ax.set_title("Volume lifted per workout")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume (kg)")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_top_exercises(sets: pd.DataFrame, out_path: Path, top_n: int = 8) -> None:
    by_volume = named_sets(sets).groupby("exercise")["volume_kg"].sum().sort_values().tail(top_n)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.barh(by_volume.index, by_volume.values)
    ax.set_title(f"Top {len(by_volume)} exercises by volume")
    ax.set_xlabel("Volume (kg)")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_progression(sets: pd.DataFrame, sessions: pd.DataFrame, out_path: Path) -> str:
    """Heaviest set per workout for the exercise with the most total volume."""
    named = named_sets(sets)
    exercise = named.groupby("exercise")["volume_kg"].sum().idxmax()
    per_workout = (
        named[named["exercise"] == exercise]
        .groupby("file_number")["weight_kg"]
        .max()
        .rename("weight_kg")
    )
    progression = sessions.join(per_workout, on="file_number").dropna(subset=["weight_kg"])

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(progression["start_time"], progression["weight_kg"], marker="o")
    ax.set_title(f"Heaviest set per workout — {exercise}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weight (kg)")
    # No zero baseline here: this is a line chart of working weights, and the
    # interesting range is where the weights actually sit. Bars get a zero
    # baseline (see plot_volume_per_session); lines don't need one.
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return exercise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Path to a Cordelia SQLite database (default: the bundled strength training example)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / "strength-training",
        help="Directory to write plots to",
    )
    parser.add_argument(
        "--locale",
        default="en",
        choices=LOCALES,
        help="Locale for exercise names read from better_labels_lookup (default: en)",
    )
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(args.db)
    try:
        sessions = load_sessions(conn)
        if sessions.empty:
            raise SystemExit(f"No sessions found in {args.db}")

        all_sets = load_sets(conn, args.locale)
        if all_sets.empty:
            raise SystemExit(f"No sets found in {args.db} — is this a strength training database?")
        sets = add_volume(working_sets(all_sets))

        print_summary(sessions, sets, all_sets)
        print_exercise_breakdown(sets, sessions)

        plot_volume_per_session(volume_per_session(sets, sessions), args.out_dir / "volume_per_session.png")
        plot_top_exercises(sets, args.out_dir / "top_exercises_by_volume.png")
        plot_progression(sets, sessions, args.out_dir / "progression.png")
    finally:
        conn.close()

    print(f"\nPlots written to {args.out_dir}/")


if __name__ == "__main__":
    main()
