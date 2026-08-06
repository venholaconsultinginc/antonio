"""Generate a synthetic Cordelia-schema-compatible dataset: eight ~5.9 km out-and-back kayak
paddles along a real route off Mayne Island, BC, on 2026-09-04/06/11/13/18/20/26/27, starting
~9am (+/-10%), with +/-10% daily variation in pace, heart rate, stroke cadence, and temperature.
Pace/heart-rate baselines and device/schema population fidelity come from a real reference paddle,
not guessed -- see docs/plan.md and data/SOURCES.md. Writes a real SQLite database directly (schema
+ data, via cordelia_db.py's sqlite3-backed helpers), same approach as the other two generators --
no intermediate SQL text file, no separate `sqlite3 ... <` step:

    python3 generate_sample_data_kayak.py             # writes output/sample_data_kayak.sqlite

See docs/plan.md (Phase 2c) for the design, and cordelia_db.py for the schema/encoding details
this script depends on.
"""

import argparse
import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import cordelia_db as cdb
from generate_sample_data import Route, load_route

REPO_ROOT = Path(__file__).parent
DEFAULT_ROUTE = REPO_ROOT / "data" / "route_kayak.gpx"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "sample_data_kayak.sqlite"
DEFAULT_PADDLE_DATES = [
    date(2026, 9, 4),
    date(2026, 9, 6),
    date(2026, 9, 11),
    date(2026, 9, 13),
    date(2026, 9, 18),
    date(2026, 9, 20),
    date(2026, 9, 26),
    date(2026, 9, 27),
]

GARMIN_MANUFACTURER_ID = 1  # Garmin, FIT manufacturer enum

# Real Garmin-assigned FIT garmin_product code -- ground truth, read directly from a real
# Cordelia-imported paddle recorded on this exact watch (see data/SOURCES.md). Serial number is
# fabricated, not the real unit's real serial.
VENU_PRODUCT_ID = 3226
VENU_SERIAL_NUMBER = 622000456  # fabricated; not the real unit's serial
VENU_SOFTWARE_VERSION = 7.80  # firmware version string, not personally identifying; reused as-is
DEVICE_PRODUCT_NAME = "Venu"

# FIT Sport enum. sport_id=41 is FIT's dedicated Kayaking code. The real reference activity was
# actually recorded as sport_id=15 (Rowing)/"Row" -- plausible, since a lot of Garmin watches
# don't have a distinct kayak activity profile -- but this repo's data is explicitly meant to be
# a kayaking example, so sport_id=41 is used deliberately instead of mirroring the reference here.
# sub_sport_id=0 (generic) rather than FIT_SUB_SPORT_WHITEWATER=41, since this is a calm coastal
# out-and-back paddle, not whitewater.
SPORT_KAYAKING = 41
SUB_SPORT_GENERIC = 0
FILE_TYPE_ACTIVITY = 4

# Event table's own timer start/stop rows -- confirmed real data, same constants as the other two
# generators (this part is protocol-level, not sport-specific).
EVENT_ID_TIMER = 0
EVENT_TYPE_START = 0
EVENT_TYPE_STOP_ALL = 4

# Session/Lap/Activity's own event_id/event_type (which FIT message closed them out) -- also
# protocol-level, confirmed real data, same values used in the other two generators.
SESSION_EVENT_ID = 8
LAP_EVENT_ID = 9
ACTIVITY_EVENT_ID = 26
EVENT_TYPE_STOP = 1

# The real reference ride auto-lapped every 500 m (11 auto-laps plus a final short one). This repo
# models one lap per activity instead, same "keep it simple" simplification the other two
# generators already make -- lap_trigger=7 (session-end), not a distance boundary.
LAP_TRIGGER_SESSION_END = 7

BASE_START_MINUTES = 9 * 60  # ~9:00 am

# Pace/heart-rate/cadence baselines come directly from the real reference paddle's own Session
# summary (enhanced_avg_speed 1.056 m/s, avg_heart_rate 121, avg_cadence 22 strokes/min) -- not
# invented, same "assume the paddler follows a similar pace" approach as the cycling generator.
BASE_SPEED_MPS = 1.056
BASE_HEART_RATE = 121
BASE_CADENCE = 22  # strokes/min

# Not from the reference paddle (a real device that reported flat 0 for Temperature/Altitude the
# entire activity -- it simply doesn't measure them for this activity type on the water); a
# plausible September-Mayne-Island-morning assumption instead, same status as the other two
# generators' invented baselines.
BASE_TEMPERATURE_C = 17.0

# Wind has no column anywhere in Cordelia's schema (checked every table in the real reference
# database, not just the seven this repo normally touches) -- so it's modeled purely as an
# unrecorded effect on pace and heart rate, not stored anywhere. Each day gets one signed
# WIND_STRENGTH_RANGE draw representing a single prevailing wind for that day: positive means a
# tailwind on the way out (and therefore a headwind on the way back), negative the reverse. This
# is a simple asymmetric-legs model, not a real wind/drag physics simulation.
WIND_STRENGTH_RANGE = 0.10


def jitter(rng: random.Random, fraction: float = 0.10) -> float:
    """A uniform +/-`fraction` relative multiplier, e.g. jitter(rng) for the +/-10% requirement."""
    return 1.0 + rng.uniform(-fraction, fraction)


def simulate_paddle(rng: random.Random, route: Route, paddle_date: date) -> dict:
    start_minutes = BASE_START_MINUTES * jitter(rng)
    start_dt = datetime.combine(paddle_date, datetime.min.time()) + timedelta(minutes=start_minutes)

    target_speed_mps = BASE_SPEED_MPS * jitter(rng)
    day_hr_factor = jitter(rng)
    day_cadence_factor = jitter(rng)
    day_temp_c = BASE_TEMPERATURE_C * jitter(rng)

    # One prevailing wind for the whole day -- see WIND_STRENGTH_RANGE's comment above. Positive
    # wind_factor: tailwind out, headwind back. Negative: the reverse.
    wind_factor = rng.uniform(-WIND_STRENGTH_RANGE, WIND_STRENGTH_RANGE)
    halfway_m = route.length_m / 2.0

    samples = []
    t = 0
    distance = 0.0
    while distance < route.length_m:
        on_return_leg = distance >= halfway_m
        leg_speed_mult = (1.0 - wind_factor) if on_return_leg else (1.0 + wind_factor)
        # Paddling into the wind takes more effort for the same boat speed than paddling with
        # it -- so heart rate moves opposite to the speed boost/penalty each leg gets.
        leg_hr_mult = (1.0 + wind_factor * 0.5) if on_return_leg else (1.0 - wind_factor * 0.5)

        # Light second-to-second noise on top of the day's target pace, so the pace trend isn't a
        # perfectly flat line within a paddle -- distance is the running integral of this, so
        # Speed and Distance stay internally consistent.
        speed = target_speed_mps * leg_speed_mult * jitter(rng, 0.03)
        distance = min(route.length_m, distance + speed)
        lat, lon, ele = route.position_at(distance)

        target_hr = BASE_HEART_RATE * day_hr_factor * leg_hr_mult
        if t < 300:  # ~5 minute warmup ramp from a resting-ish 90 bpm
            heart_rate = 90 + (target_hr - 90) * (t / 300)
        else:
            heart_rate = target_hr
        heart_rate += rng.uniform(-3, 3)

        cadence = BASE_CADENCE * day_cadence_factor + rng.uniform(-2, 2)
        temperature_c = day_temp_c + rng.uniform(-1, 1)

        samples.append(
            {
                "t": t,
                "timestamp": start_dt + timedelta(seconds=t),
                "distance": distance,
                "lat": lat,
                "lon": lon,
                "speed": speed,
                "heart_rate": heart_rate,
                "cadence": max(0.0, cadence),
                "temperature_c": temperature_c,
            }
        )
        t += 1

    duration_s = t
    end_dt = start_dt + timedelta(seconds=duration_s)
    return {"start_dt": start_dt, "end_dt": end_dt, "duration_s": duration_s, "samples": samples}


def write_paddle(conn: sqlite3.Connection, paddle_index: int, run: dict) -> None:
    """Insert one paddle into `conn`. `paddle_index` (1-based) is only used for the cosmetic
    FileID.path label -- the real `file_number` foreign-key value used everywhere else comes back
    from the FileID insert itself.
    """
    start_dt, end_dt, samples = run["start_dt"], run["end_dt"], run["samples"]
    duration_s = run["duration_s"]
    start_ts = cdb.to_iso8601(start_dt)
    end_ts = cdb.to_iso8601(end_dt)

    speeds = [s["speed"] for s in samples]
    heart_rates = [s["heart_rate"] for s in samples]
    cadences = [s["cadence"] for s in samples]
    temps = [s["temperature_c"] for s in samples]
    total_distance = samples[-1]["distance"]
    # Rough estimate, ~350 kcal/hour for recreational-pace paddling -- correlated with duration
    # rather than distance, since kayaking effort at a slow pace doesn't scale with distance the
    # way running/cycling calorie estimates do. Not a physiological model, same caveat as the
    # other two generators' calorie estimates.
    total_calories = round((duration_s / 3600.0) * 350)
    # Strokes accumulate at `cadence` (strokes/min) per second of paddling -- an internally
    # consistent running integral, same principle as Speed/Distance above.
    total_strokes = round(sum(s["cadence"] for s in samples) / 60.0)

    first_lat, first_lon = samples[0]["lat"], samples[0]["lon"]
    last_lat, last_lon = samples[-1]["lat"], samples[-1]["lon"]

    file_number = cdb.insert_row(
        conn,
        "FileID",
        {
            "Type": FILE_TYPE_ACTIVITY,
            "manufacturer_id": GARMIN_MANUFACTURER_ID,
            "garmin_product_id": VENU_PRODUCT_ID,
            "serial_number": VENU_SERIAL_NUMBER,
            "time_created": start_ts,
            "product_name": DEVICE_PRODUCT_NAME,
            "path": f"synthetic/antonio_kayak_{paddle_index:02d}.fit",
            "imported_at": cdb.to_iso8601(end_dt + timedelta(minutes=30)),
        },
    )

    cdb.insert_row(
        conn,
        "Sport",
        {
            "file_number": file_number,
            "sport_id": SPORT_KAYAKING,
            "sub_sport_id": SUB_SPORT_GENERIC,
            "Name": "Kayaking",
        },
    )

    cdb.insert_row(
        conn,
        "Activity",
        {
            "file_number": file_number,
            "Timestamp": end_ts,
            "total_timer_time": float(duration_s),
            "num_sessions": 1,
            "event_id": ACTIVITY_EVENT_ID,
            "event_type": EVENT_TYPE_STOP,
            "event_group": 0,
        },
    )

    cdb.insert_row(
        conn,
        "Event",
        {
            "file_number": file_number,
            "Timestamp": start_ts,
            "event_id": EVENT_ID_TIMER,
            "event_type": EVENT_TYPE_START,
            "event_group": 0,
        },
    )
    cdb.insert_row(
        conn,
        "Event",
        {
            "file_number": file_number,
            "Timestamp": end_ts,
            "event_id": EVENT_ID_TIMER,
            "event_type": EVENT_TYPE_STOP_ALL,
            "event_group": 0,
        },
    )

    # Two DeviceInfo rows, matching the real reference paddle's two clearly-identified rows: the
    # Venu itself, and its own internal sub-device. The real reference also logged six more rows
    # for unidentified/no-vendor ANT accessories (manufacturer_id=0, no product code) -- not
    # replicated here, same "keep it simple" simplification the cycling generator already makes
    # for its own real reference's messier details.
    device_info_rows = [
        {
            "file_number": file_number,
            "Timestamp": start_ts,
            "device_index": 0,
            "manufacturer_id": GARMIN_MANUFACTURER_ID,
            "serial_number": VENU_SERIAL_NUMBER,
            "garmin_product_id": VENU_PRODUCT_ID,
            "software_version": VENU_SOFTWARE_VERSION,
            "product_name": DEVICE_PRODUCT_NAME,
            "source_type": 5,
            "battery_level": 76,
        },
        {
            "file_number": file_number,
            "Timestamp": start_ts,
            "device_index": 1,
            "device_type": 4,
            "local_device_type": 4,
            "manufacturer_id": GARMIN_MANUFACTURER_ID,
            "serial_number": 0,
            "garmin_product_id": VENU_PRODUCT_ID,
            "software_version": VENU_SOFTWARE_VERSION,
            "source_type": 5,
        },
    ]
    for row in device_info_rows:
        cdb.insert_row(conn, "DeviceInfo", row)

    # event_id/event_type excluded here -- Session and Lap each need their own message-specific
    # value (see SESSION_EVENT_ID/LAP_EVENT_ID above). avg/max_speed (legacy) and every altitude
    # summary field are deliberately omitted: the real reference paddle doesn't populate any of
    # them either (only enhanced_avg/max_speed for speed; Altitude/enhanced_altitude are flat 0
    # for the entire real activity -- this watch doesn't report elevation on the water). gps_accuracy
    # is 0 for the same reason -- confirmed flat across the whole real reference.
    session_lap_common = {
        "file_number": file_number,
        "message_index": 0,
        "Timestamp": end_ts,
        "start_position_lat": cdb.degrees_to_semicircles(first_lat),
        "start_position_long": cdb.degrees_to_semicircles(first_lon),
        "end_position_lat": cdb.degrees_to_semicircles(last_lat),
        "end_position_long": cdb.degrees_to_semicircles(last_lon),
        "total_elapsed_time": float(duration_s),
        "total_timer_time": float(duration_s),
        "total_distance": total_distance,
        "total_calories": total_calories,
        "total_strokes": total_strokes,
        "total_cycles": total_strokes,
        "avg_heart_rate": round(sum(heart_rates) / len(heart_rates)),
        "max_heart_rate": round(max(heart_rates)),
        "avg_cadence": round(sum(cadences) / len(cadences)),
        "max_cadence": round(max(cadences)),
        "avg_temperature": round(sum(temps) / len(temps)),
        "max_temperature": round(max(temps)),
        "min_temperature": round(min(temps)),
        "enhanced_avg_speed": sum(speeds) / len(speeds),
        "enhanced_max_speed": max(speeds),
        "sport_id": SPORT_KAYAKING,
        "sub_sport_id": SUB_SPORT_GENERIC,
        "gps_accuracy": 0,
        "event_group": 0,
    }

    cdb.insert_row(
        conn,
        "Session",
        {
            **session_lap_common,
            "event_id": SESSION_EVENT_ID,
            "event_type": EVENT_TYPE_STOP,
            # ISO 8601 TEXT, same encoding as Timestamp -- see cordelia_db.py.
            "start_time": start_ts,
            "min_heart_rate": round(min(heart_rates)),
            "num_laps": 1,
            "first_lap_index": 0,
            "sport_profile_name": "Kayaking",
        },
    )

    cdb.insert_row(
        conn,
        "Lap",
        {
            **session_lap_common,
            "event_id": LAP_EVENT_ID,
            "event_type": EVENT_TYPE_STOP,
            # ISO 8601 TEXT, same as Session.start_time -- both were historically inconsistent
            # (cordelia ticket #72), now uniformly fixed. See cordelia_db.py.
            "start_time": start_ts,
            "lap_trigger": LAP_TRIGGER_SESSION_END,
        },
    )

    # Power has no meter on a kayak paddle -- explicit 0, not NULL, matching the real reference
    # (which reports 0 for every Record row, same explicit-0-not-NULL pattern the cycling
    # generator already follows for its own unequipped sensors). Altitude/enhanced_altitude are 0
    # for the same real-device-doesn't-report-it reason noted above; Speed (legacy) is 0, only
    # enhanced_speed carries the real value, also matching the real reference exactly.
    record_columns = [
        "file_number",
        "Timestamp",
        "position_lat",
        "position_long",
        "Altitude",
        "heart_rate",
        "Cadence",
        "Distance",
        "Speed",
        "Power",
        "enhanced_speed",
        "enhanced_altitude",
        "Temperature",
        "gps_accuracy",
    ]
    record_rows = [
        {
            "file_number": file_number,
            "Timestamp": cdb.to_iso8601(s["timestamp"]),
            "position_lat": cdb.degrees_to_semicircles(s["lat"]),
            "position_long": cdb.degrees_to_semicircles(s["lon"]),
            "Altitude": 0.0,
            "heart_rate": round(s["heart_rate"]),
            "Cadence": round(s["cadence"]),
            "Distance": s["distance"],
            "Speed": 0.0,
            "Power": 0,
            "enhanced_speed": s["speed"],
            "enhanced_altitude": 0.0,
            "Temperature": round(s["temperature_c"]),
            "gps_accuracy": 0,
        }
        for s in samples
    ]
    cdb.insert_many(conn, "Record", record_columns, record_rows)


def generate(paddle_dates: list[date], seed: int, route_path: Path, output_path: Path) -> None:
    """Write a fresh SQLite database to `output_path`, overwriting any existing file there. All
    data is fabricated; no real person, device, or activity is represented -- the device MODEL
    code (Venu) is real, but the serial number is not, and the route geometry is a stripped,
    personal-data-free extraction (see data/SOURCES.md).
    """
    route = Route(load_route(route_path))
    rng = random.Random(seed)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    conn = sqlite3.connect(output_path)
    try:
        cdb.create_schema(conn)
        with conn:
            for paddle_index, paddle_date in enumerate(paddle_dates, start=1):
                run = simulate_paddle(rng, route, paddle_date)
                write_paddle(conn, paddle_index, run)
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dates",
        type=lambda s: [date.fromisoformat(d.strip()) for d in s.split(",")],
        default=DEFAULT_PADDLE_DATES,
        help="comma-separated YYYY-MM-DD paddle dates (default: eight September 2026 dates)",
    )
    parser.add_argument("--seed", type=int, default=41, help="random seed, for reproducible output (default: 41)")
    parser.add_argument("--route", type=Path, default=DEFAULT_ROUTE, help="GPX route file to paddle along")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="output .sqlite database path")
    args = parser.parse_args()

    generate(args.dates, args.seed, args.route, args.output)
    print(f"wrote {len(args.dates)} paddles of {args.route.name} to {args.output} (seed={args.seed})")


if __name__ == "__main__":
    main()
