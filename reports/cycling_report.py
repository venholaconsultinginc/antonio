#!/usr/bin/env python3
"""Example visual report for a Cordelia CYCLING database.

Prints a few basic summary metrics and writes three plots: an average-speed
trend across all rides, an elevation profile for the first ride, and a GPS
route map for the first ride. Meant as a starting point to read and copy for
your own reports, not a maintained tool — see antonio's README for that
framing.

Note: Cordelia's *legacy* `Speed`/`avg_speed` columns are unpopulated for
cycling activities — this script reads `enhanced_speed`/`enhanced_avg_speed`
instead, which is where FIT actually stores it for higher-speed activities.

Usage:
    python3 reports/cycling_report.py
    python3 reports/cycling_report.py --db path/to/your.sqlite --out-dir out/
"""

import argparse
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DEFAULT_DB = Path(__file__).resolve().parent.parent / "example-data" / "cordelia-sample-cycling.sqlite"

# FIT stores latitude/longitude as 32-bit "semicircles", not degrees.
SEMICIRCLE_TO_DEGREES = 180 / 2**31


def load_sessions(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(
        """
        SELECT file_number, start_time, total_distance, total_timer_time,
               enhanced_avg_speed, avg_heart_rate, total_ascent
        FROM Session
        ORDER BY start_time
        """,
        conn,
        parse_dates=["start_time"],
    )


def load_elevation_profile(conn: sqlite3.Connection, file_number: int) -> pd.DataFrame:
    return pd.read_sql_query(
        """
        SELECT Distance, enhanced_altitude
        FROM Record
        WHERE file_number = ? AND Distance IS NOT NULL AND enhanced_altitude IS NOT NULL
        ORDER BY Timestamp
        """,
        conn,
        params=(file_number,),
    )


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


def avg_speed_kmh(sessions: pd.DataFrame) -> pd.Series:
    return sessions["enhanced_avg_speed"] * 3.6


def print_summary(sessions: pd.DataFrame) -> None:
    speed = avg_speed_kmh(sessions)
    print(f"Rides:               {len(sessions)}")
    print(f"Total distance:      {sessions['total_distance'].sum() / 1000:.1f} km")
    print(f"Total time:          {sessions['total_timer_time'].sum() / 3600:.1f} h")
    print(f"Average speed:       {speed.mean():.1f} km/h")
    print(f"Best (fastest) ride: {speed.max():.1f} km/h")
    if sessions["total_ascent"].notna().any():
        print(f"Total ascent:        {sessions['total_ascent'].sum():.0f} m")
    if sessions["avg_heart_rate"].notna().any():
        print(f"Average heart rate:  {sessions['avg_heart_rate'].mean():.0f} bpm")


def plot_speed_trend(sessions: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(sessions["start_time"], avg_speed_kmh(sessions), marker="o")
    ax.set_title("Average speed trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Average speed (km/h)")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_elevation_profile(profile: pd.DataFrame, out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.fill_between(profile["Distance"] / 1000, profile["enhanced_altitude"], color="tab:orange", alpha=0.4)
    ax.plot(profile["Distance"] / 1000, profile["enhanced_altitude"], color="tab:orange")
    ax.set_title(title)
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Elevation (m)")
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
        help="Path to a Cordelia SQLite database (default: the bundled cycling example)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output" / "cycling",
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

        plot_speed_trend(sessions, args.out_dir / "speed_trend.png")

        first_ride = sessions.iloc[0]
        first_file_number = int(first_ride["file_number"])

        profile = load_elevation_profile(conn, first_file_number)
        plot_elevation_profile(
            profile,
            args.out_dir / "elevation_profile.png",
            f"Elevation profile — {first_ride['start_time'].date()}",
        )

        track = load_track(conn, first_file_number)
        plot_route_map(track, args.out_dir / "route_map.png", f"Route — {first_ride['start_time'].date()}")
    finally:
        conn.close()

    print(f"\nPlots written to {args.out_dir}/")


if __name__ == "__main__":
    main()
