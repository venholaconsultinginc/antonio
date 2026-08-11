#!/usr/bin/env python3
"""Example visual report for a Cordelia KAYAKING database.

Prints a few basic summary metrics and writes three plots: a pace trend
across all paddles, average heart rate by five-minute bucket into the paddle
(across all paddles), and a GPS route map for the first paddle. Meant as a
starting point to read and copy for your own reports, not a maintained tool
— see antonio's README for that framing.

Usage:
    python3 reports/kayaking_report.py
    python3 reports/kayaking_report.py --db path/to/your.sqlite --out-dir out/
"""

import argparse
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DEFAULT_DB = Path(__file__).resolve().parent.parent / "example-data" / "cordelia-sample-kayaking.sqlite"

# FIT stores latitude/longitude as 32-bit "semicircles", not degrees.
SEMICIRCLE_TO_DEGREES = 180 / 2**31


def load_sessions(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(
        """
        SELECT file_number, start_time, total_distance, total_timer_time, avg_heart_rate, avg_cadence
        FROM Session
        ORDER BY start_time
        """,
        conn,
        parse_dates=["start_time"],
    )


def load_heart_rate(conn: sqlite3.Connection) -> pd.DataFrame:
    records = pd.read_sql_query(
        "SELECT file_number, Timestamp, heart_rate FROM Record WHERE heart_rate IS NOT NULL",
        conn,
        parse_dates=["Timestamp"],
    )
    paddle_start = records.groupby("file_number")["Timestamp"].transform("min")
    records["elapsed_min"] = (records["Timestamp"] - paddle_start).dt.total_seconds() / 60
    return records


def heart_rate_by_bucket(records: pd.DataFrame, bucket_minutes: int = 5) -> pd.Series:
    bucket_start = (records["elapsed_min"] // bucket_minutes * bucket_minutes).astype(int)
    return records.groupby(bucket_start)["heart_rate"].mean().sort_index()


def load_track(conn: sqlite3.Connection, file_number: int) -> pd.DataFrame:
    track = pd.read_sql_query(
        """
        SELECT position_lat, position_long
        FROM Record
        WHERE file_number = ? AND position_lat IS NOT NULL AND position_long IS NOT NULL
              AND NOT (position_lat = 0 AND position_long = 0)
        ORDER BY Timestamp
        """,
        conn,
        params=(file_number,),
    )
    track["lat"] = track["position_lat"] * SEMICIRCLE_TO_DEGREES
    track["lon"] = track["position_long"] * SEMICIRCLE_TO_DEGREES
    return track


def pace_min_per_km(sessions: pd.DataFrame) -> pd.Series:
    return (sessions["total_timer_time"] / 60) / (sessions["total_distance"] / 1000)


def avg_stroke_rate(sessions: pd.DataFrame) -> float:
    return sessions["avg_cadence"].mean()


def print_summary(sessions: pd.DataFrame) -> None:
    pace = pace_min_per_km(sessions)
    print(f"Paddles:             {len(sessions)}")
    print(f"Total distance:      {sessions['total_distance'].sum() / 1000:.1f} km")
    print(f"Total time:          {sessions['total_timer_time'].sum() / 3600:.1f} h")
    print(f"Average pace:        {pace.mean():.2f} min/km")
    print(f"Best (fastest) pace: {pace.min():.2f} min/km")
    if sessions["avg_cadence"].notna().any():
        print(f"Average stroke rate: {avg_stroke_rate(sessions):.0f} strokes/min")
    if sessions["avg_heart_rate"].notna().any():
        print(f"Average heart rate:  {sessions['avg_heart_rate'].mean():.0f} bpm")


def plot_pace_trend(sessions: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(sessions["start_time"], pace_min_per_km(sessions), marker="o")
    ax.set_title("Pace trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Pace (min/km)")
    ax.invert_yaxis()  # faster paddles (lower pace) plot higher, reads as "improvement"
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_heart_rate_by_bucket(hr_by_bucket: pd.Series, bucket_minutes: int, out_path: Path) -> None:
    labels = [f"{start}–{start + bucket_minutes}" for start in hr_by_bucket.index]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, hr_by_bucket.values)
    ax.set_title("Average heart rate by time into the paddle")
    ax.set_xlabel("Minutes into the paddle")
    ax.set_ylabel("Average heart rate (bpm)")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_route_map(track: pd.DataFrame, out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(track["lon"], track["lat"])
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Path to a Cordelia SQLite database (default: the bundled kayaking example)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / "kayaking",
        help="Directory to write plots to",
    )
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(args.db)
    try:
        sessions = load_sessions(conn)
        if sessions.empty:
            raise SystemExit(f"No sessions found in {args.db}")

        print_summary(sessions)

        plot_pace_trend(sessions, args.out_dir / "pace_trend.png")

        bucket_minutes = 5
        hr_records = load_heart_rate(conn)
        hr_by_bucket = heart_rate_by_bucket(hr_records, bucket_minutes)
        plot_heart_rate_by_bucket(hr_by_bucket, bucket_minutes, args.out_dir / "heart_rate_by_bucket.png")

        first_paddle = sessions.iloc[0]
        track = load_track(conn, int(first_paddle["file_number"]))
        plot_route_map(track, args.out_dir / "route_map.png", f"Route — {first_paddle['start_time'].date()}")
    finally:
        conn.close()

    print(f"\nPlots written to {args.out_dir}/")


if __name__ == "__main__":
    main()
