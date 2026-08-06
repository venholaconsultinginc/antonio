"""Generate a synthetic Cordelia-schema-compatible dataset: four ~77 km road-cycling rides along
the real Tour de Victoria 80km route, on 2026-09-05/12/18/26, starting ~9am (+/-10%), with +/-10%
daily variation in pace, heart rate, and temperature. Pace/HR baselines and device/schema fidelity
(which fields a real Edge 1040 + paired Venu 4 actually populate) come from a real reference ride,
not guessed -- see docs/plan.md and data/SOURCES.md. Writes plain SQL INSERT statements to a text
file, same approach as generate_sample_data.py -- it does not open or write to a SQLite database
directly:

    python3 generate_sample_data_bike.py             # writes output/sample_data_bike.sql

    sqlite3 mydb.sqlite < sql/create_tables.sql       # create the schema (idempotent, safe to
    sqlite3 mydb.sqlite < output/sample_data_bike.sql # rerun if already applied for running data)

See docs/plan.md (Phase 2b) for the design, and cordelia_db.py for the schema/encoding details
this script depends on.
"""

import argparse
import math
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import cordelia_db as cdb
from generate_sample_data import Route, load_route

REPO_ROOT = Path(__file__).parent
DEFAULT_ROUTE = REPO_ROOT / "data" / "route_bike.gpx"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "sample_data_bike.sql"
DEFAULT_RIDE_DATES = [date(2026, 9, 5), date(2026, 9, 12), date(2026, 9, 18), date(2026, 9, 26)]

GARMIN_MANUFACTURER_ID = 1  # Garmin, FIT manufacturer enum

# Real Garmin-assigned FIT garmin_product codes -- unlike the running generator's placeholder
# Forerunner 970 ID, these are ground truth, read directly from a real Cordelia-imported ride
# recorded on this exact hardware pairing (see data/SOURCES.md). Serial numbers are fabricated,
# not the real ride's real device serials -- those identify a real physical unit.
EDGE_1040_PRODUCT_ID = 3843
VENU_4_PRODUCT_ID = 3865
GENERIC_ANT_PRODUCT_ID = 255  # FIT sentinel for an ANT+ device with no reported product code
ANTPLUS_DEVICE_TYPE_HEART_RATE = 120  # ANT+ device profile number for a heart rate monitor

EDGE_SERIAL_NUMBER = 104000555  # fabricated; not the real unit's serial
HR_SENSOR_SERIAL_NUMBER = 55000777  # fabricated; not the real unit's serial
EDGE_SOFTWARE_VERSION = 31.33  # firmware version string, not personally identifying; reused as-is
VENU_SOFTWARE_VERSION = 16.01
HR_SENSOR_SOFTWARE_VERSION = 17.30
DEVICE_PRODUCT_NAME = "Edge 1040"

# FIT Sport enum -- confirmed against real data (not guessed, unlike the running generator's
# sport_id=1, which -- for running -- happens to also be the well-documented value).
SPORT_CYCLING = 2
SUB_SPORT_ROAD = 7
SPORT_PROFILE_NAME = "ROAD"
FILE_TYPE_ACTIVITY = 4

# Event table's own timer start/stop rows -- confirmed real data, same constants as the running
# generator (this part is protocol-level, not sport-specific).
EVENT_ID_TIMER = 0
EVENT_TYPE_START = 0
EVENT_TYPE_STOP_ALL = 4

# Session/Lap/Activity's own event_id/event_type (which FIT message closed them out) -- also
# protocol-level, confirmed real data, same values used in the running generator after its fix.
SESSION_EVENT_ID = 8
LAP_EVENT_ID = 9
ACTIVITY_EVENT_ID = 26
EVENT_TYPE_STOP = 1

# FIT lap_trigger enum: this repo models one lap per ride (see docs/plan.md's "keep it simple"
# note), so the lap ends because the session/activity itself ends, not a manual button press or
# an auto-lap distance boundary (lap_trigger=2, which the real reference ride actually used, with
# an auto-lap every 5 km -- not replicated here).
LAP_TRIGGER_SESSION_END = 7

BASE_START_MINUTES = 9 * 60  # ~9:00 am

# Pace/HR baselines come directly from the real reference ride's own Session summary (avg_speed
# 6.15 m/s via enhanced_avg_speed, avg_heart_rate 155), per "assume the rider follows a similar
# pace, heart rate" -- not invented the way the running generator's baselines were.
BASE_SPEED_MPS = 6.15
BASE_HEART_RATE = 155

# Not from the reference ride (that was an August afternoon; these are September Victoria, BC
# mornings) -- a plausible seasonal baseline instead. Documented assumption, not measured.
BASE_TEMPERATURE_C = 15.0


def jitter(rng: random.Random, fraction: float = 0.10) -> float:
    """A uniform +/-`fraction` relative multiplier, e.g. jitter(rng) for the +/-10% requirement."""
    return 1.0 + rng.uniform(-fraction, fraction)


def simulate_ride(rng: random.Random, route: Route, ride_date: date) -> dict:
    start_minutes = BASE_START_MINUTES * jitter(rng)
    start_dt = datetime.combine(ride_date, datetime.min.time()) + timedelta(minutes=start_minutes)

    target_speed_mps = BASE_SPEED_MPS * jitter(rng)
    day_hr_factor = jitter(rng)
    day_temp_c = BASE_TEMPERATURE_C * jitter(rng)

    samples = []
    t = 0
    distance = 0.0
    while distance < route.length_m:
        # Light second-to-second noise on top of the day's target pace, so the pace trend isn't a
        # perfectly flat line within a ride -- distance is the running integral of this, so Speed
        # and Distance stay internally consistent.
        speed = target_speed_mps * jitter(rng, 0.03)
        distance = min(route.length_m, distance + speed)
        lat, lon, ele = route.position_at(distance)

        target_hr = BASE_HEART_RATE * day_hr_factor
        if t < 300:  # ~5 minute warmup ramp from a resting-ish 100 bpm
            heart_rate = 100 + (target_hr - 100) * (t / 300)
        else:
            heart_rate = target_hr
        heart_rate += rng.uniform(-3, 3)

        temperature_c = day_temp_c + rng.uniform(-1, 1)

        samples.append(
            {
                "t": t,
                "timestamp": start_dt + timedelta(seconds=t),
                "distance": distance,
                "lat": lat,
                "lon": lon,
                "ele": ele,
                "speed": speed,
                "heart_rate": heart_rate,
                "temperature_c": temperature_c,
            }
        )
        t += 1

    duration_s = t
    end_dt = start_dt + timedelta(seconds=duration_s)
    return {"start_dt": start_dt, "end_dt": end_dt, "duration_s": duration_s, "samples": samples}


def build_ride_statements(file_number: int, run: dict) -> list[str]:
    start_dt, end_dt, samples = run["start_dt"], run["end_dt"], run["samples"]
    duration_s = run["duration_s"]
    start_ts = cdb.to_iso8601(start_dt)
    end_ts = cdb.to_iso8601(end_dt)
    start_garmin = cdb.unix_to_garmin_time(cdb.naive_utc_to_unix(start_dt))

    speeds = [s["speed"] for s in samples]
    heart_rates = [s["heart_rate"] for s in samples]
    temps = [s["temperature_c"] for s in samples]
    elevations = [s["ele"] for s in samples]
    total_distance = samples[-1]["distance"]
    total_ascent = sum(max(0.0, b - a) for a, b in zip(elevations, elevations[1:]))
    total_descent = sum(max(0.0, a - b) for a, b in zip(elevations, elevations[1:]))
    # Rough estimate, ~30 kcal/km for recreational road cycling (lower than running's per-km
    # cost since cycling is more efficient) -- not a physiological model.
    total_calories = round((total_distance / 1000.0) * 30)

    first_lat, first_lon = samples[0]["lat"], samples[0]["lon"]
    last_lat, last_lon = samples[-1]["lat"], samples[-1]["lon"]

    statements = []

    statements.append(
        cdb.insert_statement(
            "FileID",
            {
                "file_number": file_number,
                "Type": FILE_TYPE_ACTIVITY,
                "manufacturer_id": GARMIN_MANUFACTURER_ID,
                "garmin_product_id": EDGE_1040_PRODUCT_ID,
                "serial_number": EDGE_SERIAL_NUMBER,
                "time_created": start_ts,
                "path": f"synthetic/antonio_bike_{file_number:02d}.fit",
                "imported_at": cdb.to_iso8601(end_dt + timedelta(minutes=30)),
            },
        )
    )

    statements.append(
        cdb.insert_statement(
            "FileCreator",
            {"file_number": file_number, "software_version": 3133, "hardware_version": 0},
        )
    )

    statements.append(
        cdb.insert_statement(
            "Sport",
            {
                "file_number": file_number,
                "sport_id": SPORT_CYCLING,
                "sub_sport_id": SUB_SPORT_ROAD,
                "Name": SPORT_PROFILE_NAME,
            },
        )
    )

    statements.append(
        cdb.insert_statement(
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
    )

    statements.append(
        cdb.insert_statement(
            "Event",
            {
                "file_number": file_number,
                "Timestamp": start_ts,
                "event_id": EVENT_ID_TIMER,
                "event_type": EVENT_TYPE_START,
                "event_group": 0,
            },
        )
    )
    statements.append(
        cdb.insert_statement(
            "Event",
            {
                "file_number": file_number,
                "Timestamp": end_ts,
                "event_id": EVENT_ID_TIMER,
                "event_type": EVENT_TYPE_STOP_ALL,
                "event_group": 0,
            },
        )
    )

    # Four DeviceInfo rows, matching the real reference ride's pairing structure: the Edge 1040
    # itself, an internal Edge sub-device, the Venu 4's own (BLE) identity, and the Venu 4's ANT+
    # heart-rate broadcast to the Edge (a logically separate "device" in FIT, generic product code
    # since ANT+ HR broadcasts don't carry a model number). Not duplicated mid-ride -- see
    # docs/plan.md's "keep it simple" note; the real ride has this same set twice.
    device_info_rows = [
        {
            "file_number": file_number,
            "Timestamp": start_ts,
            "device_index": 0,
            "manufacturer_id": GARMIN_MANUFACTURER_ID,
            "serial_number": EDGE_SERIAL_NUMBER,
            "garmin_product_id": EDGE_1040_PRODUCT_ID,
            "software_version": EDGE_SOFTWARE_VERSION,
            "source_type": 5,
            "battery_voltage": 0.0,
            "battery_status": 0,
            "battery_level": 0,
        },
        {
            "file_number": file_number,
            "Timestamp": start_ts,
            "device_index": 1,
            "device_type": 4,
            "local_device_type": 4,
            "manufacturer_id": GARMIN_MANUFACTURER_ID,
            "serial_number": 0,
            "garmin_product_id": EDGE_1040_PRODUCT_ID,
            "software_version": EDGE_SOFTWARE_VERSION,
            "source_type": 5,
            "battery_voltage": 0.0,
            "battery_status": 0,
            "battery_level": 0,
        },
        {
            "file_number": file_number,
            "Timestamp": start_ts,
            "device_index": 2,
            "manufacturer_id": GARMIN_MANUFACTURER_ID,
            "serial_number": 0,
            "garmin_product_id": VENU_4_PRODUCT_ID,
            "software_version": VENU_SOFTWARE_VERSION,
            "source_type": 5,
            "battery_voltage": 0.0,
            "battery_status": 0,
            "battery_level": 0,
        },
        {
            "file_number": file_number,
            "Timestamp": start_ts,
            "device_index": 3,
            "device_type": ANTPLUS_DEVICE_TYPE_HEART_RATE,
            "antplus_device_type": ANTPLUS_DEVICE_TYPE_HEART_RATE,
            "manufacturer_id": GARMIN_MANUFACTURER_ID,
            "serial_number": HR_SENSOR_SERIAL_NUMBER,
            "garmin_product_id": GENERIC_ANT_PRODUCT_ID,
            "software_version": HR_SENSOR_SOFTWARE_VERSION,
            "ant_network": 1,
            "source_type": 1,
            "battery_voltage": round(rng_battery_voltage(file_number), 3),
            "battery_status": 2,
            "battery_level": 90 - file_number * 4,  # mild plausible drain across the month
        },
    ]
    for row in device_info_rows:
        statements.append(cdb.insert_statement("DeviceInfo", row))

    # event_id/event_type excluded here -- Session and Lap each need their own message-specific
    # value (see SESSION_EVENT_ID/LAP_EVENT_ID above). avg/max_speed, avg/max_cadence,
    # avg/max_power, and all altitude summary fields are deliberately omitted: the real reference
    # ride doesn't populate any of them either (only enhanced_avg/max_speed for speed, and no
    # altitude summary at all -- total_ascent/total_descent are the only elevation figures it
    # carries). Likewise, min_heart_rate, total_training_effect, total_anaerobic_training_effect,
    # avg_vam, and training_load_peak are Garmin's own derived/computed metrics, not
    # directly-measured data -- out of scope to fake convincingly, so left unset.
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
        "avg_heart_rate": round(sum(heart_rates) / len(heart_rates)),
        "max_heart_rate": round(max(heart_rates)),
        "total_ascent": round(total_ascent),
        "total_descent": round(total_descent),
        "avg_temperature": round(sum(temps) / len(temps)),
        "max_temperature": round(max(temps)),
        "min_temperature": round(min(temps)),
        "enhanced_avg_speed": sum(speeds) / len(speeds),
        "enhanced_max_speed": max(speeds),
        "sport_id": SPORT_CYCLING,
        "sub_sport_id": SUB_SPORT_ROAD,
        "event_group": 0,
    }

    statements.append(
        cdb.insert_statement(
            "Session",
            {
                **session_lap_common,
                "event_id": SESSION_EVENT_ID,
                "event_type": EVENT_TYPE_STOP,
                # ISO 8601 TEXT despite the INTEGER column declaration -- see cordelia_db.py's
                # GARMIN_EPOCH_OFFSET comment and docs/plan.md.
                "start_time": start_ts,
                "nec_lat": cdb.degrees_to_semicircles(max(s["lat"] for s in samples)),
                "nec_long": cdb.degrees_to_semicircles(max(s["lon"] for s in samples)),
                "swc_lat": cdb.degrees_to_semicircles(min(s["lat"] for s in samples)),
                "swc_long": cdb.degrees_to_semicircles(min(s["lon"] for s in samples)),
                "num_laps": 1,
                "first_lap_index": 0,
                "sport_profile_name": SPORT_PROFILE_NAME,
                "gps_accuracy": 0,
            },
        )
    )

    statements.append(
        cdb.insert_statement(
            "Lap",
            {
                **session_lap_common,
                "event_id": LAP_EVENT_ID,
                "event_type": EVENT_TYPE_STOP,
                # Garmin-epoch INTEGER despite the TEXT column declaration -- confirmed
                # cordelia/src/records/lap.cpp:903,1426. See docs/plan.md.
                "start_time": start_garmin,
                "lap_trigger": LAP_TRIGGER_SESSION_END,
            },
        )
    )

    # Power and Cadence, and the legacy Speed/Altitude fields, are written as explicit 0 (not
    # left NULL) to match exactly what a real Edge 1040 without a power meter or cadence sensor
    # writes -- confirmed against the real reference ride, where all four are 0 for every single
    # Record row. gps_accuracy is 0 for the same reason. Only enhanced_speed/enhanced_altitude
    # carry the real values.
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
            "Cadence": 0,
            "Distance": s["distance"],
            "Speed": 0.0,
            "Power": 0,
            "enhanced_speed": s["speed"],
            "enhanced_altitude": s["ele"],
            "Temperature": round(s["temperature_c"]),
            "gps_accuracy": 0,
        }
        for s in samples
    ]
    statements.append(cdb.insert_many_statement("Record", record_columns, record_rows))

    return statements


def rng_battery_voltage(file_number: int) -> float:
    """Deterministic-looking mild battery drain across the four rides -- not randomized, since
    it's cosmetic flavor rather than something worth spending the RNG's sequence on."""
    return 4.20 - file_number * 0.02


def generate(ride_dates: list[date], seed: int, route_path: Path, output_path: Path) -> None:
    route = Route(load_route(route_path))
    rng = random.Random(seed)

    lines = [
        "-- Synthetic Cordelia sample data generated by generate_sample_data_bike.py.",
        f"-- {len(ride_dates)} rides of ~{route.length_m / 1000:.2f} km each along the Tour de",
        f"-- Victoria 80km route ({route_path.name}, see data/SOURCES.md), seed={seed}.",
        "-- Apply sql/create_tables.sql to an empty database before this file.",
        "-- All data is fabricated; no real person, device, or activity is represented -- device",
        "-- MODEL codes (Edge 1040 / Venu 4) are real, but serial numbers are not.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]

    for file_number, ride_date in enumerate(ride_dates, start=1):
        run = simulate_ride(rng, route, ride_date)
        lines.append(f"-- Ride {file_number}: {ride_date.isoformat()}")
        lines.extend(build_ride_statements(file_number, run))
        lines.append("")

    lines.append("COMMIT;")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dates",
        type=lambda s: [date.fromisoformat(d.strip()) for d in s.split(",")],
        default=DEFAULT_RIDE_DATES,
        help="comma-separated YYYY-MM-DD ride dates (default: 2026-09-05,09-12,09-18,09-26)",
    )
    parser.add_argument("--seed", type=int, default=1040, help="random seed, for reproducible output (default: 1040)")
    parser.add_argument("--route", type=Path, default=DEFAULT_ROUTE, help="GPX route file to ride along")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="output .sql file path")
    args = parser.parse_args()

    generate(args.dates, args.seed, args.route, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
