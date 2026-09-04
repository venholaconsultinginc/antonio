#!/usr/bin/env python3
"""Example visual report for a Cordelia SWIMMING database.

Prints a few basic summary metrics and writes three plots: a pace trend in
minutes per 100 m, distance swum per session, and the distribution of SWOLF
scores across every length. Meant as a starting point to read and copy for
your own reports, not a maintained tool — see antonio's README for that
framing.

Pool swimming has no GPS, so there is no route to map. What it has instead is
the `Length` table: one row per pool length, with its own time and stroke
count. That table doesn't appear for any other sport in this repo, and the
SWOLF plot below is built from it — see `load_lengths()`.

Usage:
    python3 reports/swimming_report.py
    python3 reports/swimming_report.py --db path/to/your.sqlite --out-dir out/
    python3 reports/swimming_report.py --locale de
"""

import argparse
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DEFAULT_DB = Path(__file__).resolve().parent.parent / "example-data" / "cordelia-sample-swimming.sqlite"

# better_labels_lookup carries every label in these six locales.
LOCALES = ("en", "fr", "es", "de", "it", "ptbr")


def load_sessions(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(
        """
        SELECT file_number, start_time, total_distance, total_timer_time,
               total_strokes, number_lengths, pool_length, avg_heart_rate
        FROM Session
        ORDER BY start_time
        """,
        conn,
        parse_dates=["start_time"],
    )


def load_lengths(conn: sqlite3.Connection, locale: str = "en") -> pd.DataFrame:
    """One row per pool length, with the stroke name resolved to readable text.

    `Length.swim_stroke` is a Garmin code, not a name. Cordelia's
    better_labels_definitions and better_labels_lookup tables translate it: the
    definition row matches on domain `swim_stroke` plus the code, and the lookup
    row supplies the text for one locale. The same pattern resolves exercise
    names in reports/strength_training_report.py.
    """
    return pd.read_sql_query(
        """
        SELECT l.file_number,
               l.start_time,
               l.total_timer_time            AS seconds,
               l.total_strokes               AS strokes,
               COALESCE(stroke_label.value, 'Unspecified') AS stroke
        FROM Length l
        LEFT JOIN better_labels_definitions stroke_def
               ON stroke_def.domain = 'swim_stroke'
              AND stroke_def.garmin_key = CAST(l.swim_stroke AS TEXT)
        LEFT JOIN better_labels_lookup stroke_label
               ON stroke_label.better_labels_id = stroke_def.better_labels_id
              AND stroke_label.locale = :locale
        WHERE l.total_timer_time IS NOT NULL
        ORDER BY l.start_time
        """,
        conn,
        params={"locale": locale},
        parse_dates=["start_time"],
    )


def add_swolf(lengths: pd.DataFrame) -> pd.DataFrame:
    """SWOLF is the swimmer's golf score: seconds for the length plus strokes taken.

    Lower is better, and it captures something pace alone misses — swimming a
    length faster by thrashing costs strokes, so the score only improves when
    speed and efficiency improve together.
    """
    lengths = lengths.copy()
    lengths["swolf"] = lengths["seconds"] + lengths["strokes"]
    return lengths


def pace_min_per_100m(sessions: pd.DataFrame) -> pd.Series:
    return (sessions["total_timer_time"] / 60) / (sessions["total_distance"] / 100)


def print_summary(sessions: pd.DataFrame, lengths: pd.DataFrame) -> None:
    pace = pace_min_per_100m(sessions)
    strokes_per_length = lengths["strokes"].mean()
    pool = sessions["pool_length"].dropna()

    print(f"Sessions:              {len(sessions)}")
    print(f"Date range:            {sessions['start_time'].min().date()} to {sessions['start_time'].max().date()}")
    print(f"Total distance:        {sessions['total_distance'].sum() / 1000:.1f} km")
    print(f"Total time:            {sessions['total_timer_time'].sum() / 3600:.1f} h")
    print(f"Average pace:          {pace.mean():.2f} min/100 m")
    print(f"Best (fastest) pace:   {pace.min():.2f} min/100 m")
    if not pool.empty:
        print(f"Pool length:           {pool.iloc[0]:.0f} m")
    print(f"Lengths swum:          {len(lengths)}")
    print(f"Total strokes:         {int(lengths['strokes'].sum()):,}")
    print(f"Average per length:    {strokes_per_length:.1f} strokes, {lengths['seconds'].mean():.1f} s")
    print(f"Average SWOLF:         {lengths['swolf'].mean():.1f}")
    if sessions["avg_heart_rate"].notna().any():
        print(f"Average heart rate:    {sessions['avg_heart_rate'].mean():.0f} bpm")

    strokes = lengths["stroke"].value_counts()
    if len(strokes) == 1:
        # Worth stating plainly rather than plotting: a one-stroke breakdown is
        # a single bar. Mixed-stroke data would make a stroke chart worthwhile.
        print(f"Stroke:                {strokes.index[0]} only, all {len(lengths)} lengths")
    else:
        summary = ", ".join(f"{name} {count}" for name, count in strokes.items())
        print(f"Strokes:               {summary}")


def plot_pace_trend(sessions: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(sessions["start_time"], pace_min_per_100m(sessions), marker="o")
    ax.set_title("Pace trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Pace (min/100 m)")
    ax.invert_yaxis()  # faster swims (lower pace) plot higher, reads as "improvement"
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_distance_per_session(sessions: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(sessions["start_time"].dt.date.astype(str), sessions["total_distance"])
    ax.set_title("Distance per session")
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (m)")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_swolf_distribution(lengths: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(lengths["swolf"], bins=25)
    ax.axvline(lengths["swolf"].mean(), linestyle="--", label=f"mean {lengths['swolf'].mean():.1f}")
    ax.set_title(f"SWOLF across all {len(lengths)} lengths")
    ax.set_xlabel("SWOLF (seconds + strokes, lower is better)")
    ax.set_ylabel("Lengths")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Path to a Cordelia SQLite database (default: the bundled swimming example)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / "swimming",
        help="Directory to write plots to",
    )
    parser.add_argument(
        "--locale",
        default="en",
        choices=LOCALES,
        help="Locale for stroke names read from better_labels_lookup (default: en)",
    )
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(args.db)
    try:
        sessions = load_sessions(conn)
        if sessions.empty:
            raise SystemExit(f"No sessions found in {args.db}")

        lengths = add_swolf(load_lengths(conn, args.locale))
        if lengths.empty:
            raise SystemExit(f"No pool lengths found in {args.db} — is this a swimming database?")

        print_summary(sessions, lengths)

        plot_pace_trend(sessions, args.out_dir / "pace_trend.png")
        plot_distance_per_session(sessions, args.out_dir / "distance_per_session.png")
        plot_swolf_distribution(lengths, args.out_dir / "swolf_distribution.png")
    finally:
        conn.close()

    print(f"\nPlots written to {args.out_dir}/")


if __name__ == "__main__":
    main()
