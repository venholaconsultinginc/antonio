"""Generate a synthetic Cordelia-schema-compatible dataset: one ~5 km run per day for N days,
along a real public route, with +/-10% daily variation in pace, heart rate, cadence, temperature,
and start time. Writes plain SQL INSERT statements to a text file -- it does not open or write to
a SQLite database directly. Load the result into a database with sql/create_tables.sql applied
first, e.g.:

    sqlite3 mydb.sqlite < sql/create_tables.sql
    sqlite3 mydb.sqlite < output/sample_data.sql

See docs/plan.md (Phase 2) for the design, and cordelia_db.py for the schema/encoding details
this script depends on.
"""

import argparse
import math
import random
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from pathlib import Path

import cordelia_db as cdb

REPO_ROOT = Path(__file__).parent
DEFAULT_ROUTE = REPO_ROOT / "data" / "route.gpx"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "sample_data.sql"

GPX_NS = "{http://www.topografix.com/GPX/1/1}"

# Garmin, FIT manufacturer enum -- well documented, not a guess.
GARMIN_MANUFACTURER_ID = 1

# Placeholder only: the real Garmin-assigned FIT garmin_product code for the Forerunner 970
# was not publicly available (not in the locally vendored FIT SDK, no authoritative public
# source found) as of 2026-08-05. Chosen to be obviously synthetic (mirrors the model number)
# rather than colliding with a real device's code. The user asked for "an imaginary device ID"
# for this exact reason -- see docs/plan.md.
FORERUNNER_970_PRODUCT_ID = 9970
DEVICE_SERIAL_NUMBER = 970000123  # fabricated; not a real unit
DEVICE_PRODUCT_NAME = "Forerunner 970"
DEVICE_SOFTWARE_VERSION = 21.34  # arbitrary, plausible

# FIT Sport/Event enums -- widely-documented, stable protocol-level values.
SPORT_RUNNING = 1
SUB_SPORT_GENERIC = 0
FILE_TYPE_ACTIVITY = 4

# The Event *table*'s own timer start/stop rows (message type "event", generic across all
# activities) -- confirmed against a real Cordelia-produced database: event_id=0 (timer),
# event_type 0 (start) and 4 (stop_all).
EVENT_ID_TIMER = 0
EVENT_TYPE_START = 0
EVENT_TYPE_STOP_ALL = 4

# By contrast, Session/Lap/Activity each carry their own event_id/event_type pair recording
# *which kind of FIT message* closed them out -- a different value per message type, not the
# generic timer constants above. Also confirmed against real data (previously guessed wrong
# here as EVENT_ID_TIMER/EVENT_TYPE_STOP_ALL for all three -- see cordelia ticket #72's
# follow-up comment and docs/plan.md).
SESSION_EVENT_ID = 8
LAP_EVENT_ID = 9
ACTIVITY_EVENT_ID = 26
EVENT_TYPE_STOP = 1

BASE_START_MINUTES = 9 * 60  # ~9:00 am
BASE_PACE_SEC_PER_KM = 5 * 60 + 45  # 5:45 min/km easy run
BASE_HEART_RATE = 150
BASE_CADENCE = 85  # strides/min, one leg (Cordelia's Cadence field), roughly 170 spm total
BASE_TEMPERATURE_C = 20.0


def load_route(path: Path) -> list[tuple[float, float, float]]:
    tree = ET.parse(path)
    points = []
    for trkpt in tree.getroot().iter(f"{GPX_NS}trkpt"):
        lat = float(trkpt.get("lat"))
        lon = float(trkpt.get("lon"))
        ele_el = trkpt.find(f"{GPX_NS}ele")
        ele = float(ele_el.text) if ele_el is not None else 0.0
        points.append((lat, lon, ele))
    if len(points) < 2:
        raise ValueError(f"{path} contains fewer than 2 track points")
    return points


def haversine_m(p1: tuple[float, float, float], p2: tuple[float, float, float]) -> float:
    lat1, lon1, _ = p1
    lat2, lon2, _ = p2
    r = 6_371_000.0  # mean Earth radius, meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class Route:
    """A GPX track treated as a single path; position_at() interpolates along it by distance."""

    def __init__(self, points: list[tuple[float, float, float]]):
        self.points = points
        self.cum_dist = [0.0]
        for a, b in zip(points, points[1:]):
            self.cum_dist.append(self.cum_dist[-1] + haversine_m(a, b))
        self.length_m = self.cum_dist[-1]

    def position_at(self, distance_m: float) -> tuple[float, float, float]:
        distance_m = max(0.0, min(distance_m, self.length_m))
        lo, hi = 0, len(self.cum_dist) - 1
        while lo < hi - 1:
            mid = (lo + hi) // 2
            if self.cum_dist[mid] <= distance_m:
                lo = mid
            else:
                hi = mid
        seg_len = self.cum_dist[hi] - self.cum_dist[lo]
        t = 0.0 if seg_len == 0 else (distance_m - self.cum_dist[lo]) / seg_len
        lat1, lon1, ele1 = self.points[lo]
        lat2, lon2, ele2 = self.points[hi]
        return (
            lat1 + (lat2 - lat1) * t,
            lon1 + (lon2 - lon1) * t,
            ele1 + (ele2 - ele1) * t,
        )


def jitter(rng: random.Random, fraction: float = 0.10) -> float:
    """A uniform +/-`fraction` relative multiplier, e.g. jitter(rng) for the +/-10% requirement."""
    return 1.0 + rng.uniform(-fraction, fraction)


def simulate_day(rng: random.Random, route: Route, run_date: date) -> dict:
    start_minutes = BASE_START_MINUTES * jitter(rng)
    start_dt = datetime.combine(run_date, datetime.min.time()) + timedelta(minutes=start_minutes)

    pace_sec_per_km = BASE_PACE_SEC_PER_KM * jitter(rng)
    target_speed_mps = 1000.0 / pace_sec_per_km

    day_hr_factor = jitter(rng)
    day_cadence_factor = jitter(rng)
    day_temp_c = BASE_TEMPERATURE_C * jitter(rng)

    samples = []
    t = 0
    distance = 0.0
    while distance < route.length_m:
        # Light second-to-second noise on top of the day's target pace, so the pace trend
        # isn't a perfectly flat line within a run -- distance is the running integral of this,
        # so Speed and Distance stay internally consistent.
        speed = target_speed_mps * jitter(rng, 0.03)
        distance = min(route.length_m, distance + speed)
        lat, lon, ele = route.position_at(distance)

        target_hr = BASE_HEART_RATE * day_hr_factor
        if t < 300:  # ~5 minute warmup ramp from a resting-ish 100 bpm
            heart_rate = 100 + (target_hr - 100) * (t / 300)
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
                "ele": ele,
                "speed": speed,
                "heart_rate": heart_rate,
                "cadence": cadence,
                "temperature_c": temperature_c,
            }
        )
        t += 1

    duration_s = t
    end_dt = start_dt + timedelta(seconds=duration_s)
    return {"start_dt": start_dt, "end_dt": end_dt, "duration_s": duration_s, "samples": samples}


def build_day_statements(file_number: int, run: dict) -> list[str]:
    start_dt, end_dt, samples = run["start_dt"], run["end_dt"], run["samples"]
    duration_s = run["duration_s"]
    start_ts = cdb.to_iso8601(start_dt)
    end_ts = cdb.to_iso8601(end_dt)
    start_garmin = cdb.unix_to_garmin_time(cdb.naive_utc_to_unix(start_dt))

    speeds = [s["speed"] for s in samples]
    heart_rates = [s["heart_rate"] for s in samples]
    cadences = [s["cadence"] for s in samples]
    temps = [s["temperature_c"] for s in samples]
    elevations = [s["ele"] for s in samples]
    total_distance = samples[-1]["distance"]
    total_ascent = sum(max(0.0, b - a) for a, b in zip(elevations, elevations[1:]))
    total_descent = sum(max(0.0, a - b) for a, b in zip(elevations, elevations[1:]))
    total_calories = round((total_distance / 1000.0) * 65)  # rough estimate, ~65 kcal/km

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
                "garmin_product_id": FORERUNNER_970_PRODUCT_ID,
                "serial_number": DEVICE_SERIAL_NUMBER,
                "time_created": start_ts,
                "product_name": DEVICE_PRODUCT_NAME,
                "path": f"synthetic/antonio_day_{file_number:02d}.fit",
                "imported_at": cdb.to_iso8601(end_dt + timedelta(minutes=30)),
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

    statements.append(
        cdb.insert_statement(
            "DeviceInfo",
            {
                "file_number": file_number,
                "Timestamp": start_ts,
                "device_index": 0,
                "manufacturer_id": GARMIN_MANUFACTURER_ID,
                "serial_number": DEVICE_SERIAL_NUMBER,
                "garmin_product_id": FORERUNNER_970_PRODUCT_ID,
                "software_version": DEVICE_SOFTWARE_VERSION,
                "product_name": DEVICE_PRODUCT_NAME,
                "battery_level": 87,
            },
        )
    )

    # event_id/event_type deliberately excluded here -- Session and Lap each need their own
    # message-specific value (see SESSION_EVENT_ID/LAP_EVENT_ID above), not a shared one.
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
        "avg_speed": sum(speeds) / len(speeds),
        "max_speed": max(speeds),
        "avg_heart_rate": round(sum(heart_rates) / len(heart_rates)),
        "max_heart_rate": round(max(heart_rates)),
        "avg_cadence": round(sum(cadences) / len(cadences)),
        "max_cadence": round(max(cadences)),
        "total_ascent": round(total_ascent),
        "total_descent": round(total_descent),
        "event_group": 0,
    }

    statements.append(
        cdb.insert_statement(
            "Session",
            {
                **session_lap_common,
                "event_id": SESSION_EVENT_ID,
                "event_type": EVENT_TYPE_STOP,
                # Declared INTEGER in the schema, but cordelia actually binds/reads this as an
                # ISO 8601 TEXT string, same encoding as Timestamp -- confirmed against a real
                # Cordelia-produced database (session.cpp:1109 bind_string, :1764
                # ISO8601DateTime::from_string). Previously written here as a Garmin-epoch
                # integer, which was wrong -- see cordelia_db.py's GARMIN_EPOCH_OFFSET comment
                # and docs/plan.md.
                "start_time": start_ts,
                "sport_id": SPORT_RUNNING,
                "sub_sport_id": SUB_SPORT_GENERIC,
                "min_heart_rate": round(min(heart_rates)),
                "avg_temperature": round(sum(temps) / len(temps)),
                "max_temperature": round(max(temps)),
                "gps_accuracy": 3,
                "avg_altitude": sum(elevations) / len(elevations),
                "max_altitude": max(elevations),
                "min_altitude": min(elevations),
                "num_laps": 1,
                "first_lap_index": 0,
                "enhanced_avg_speed": sum(speeds) / len(speeds),
                "enhanced_max_speed": max(speeds),
                "enhanced_avg_altitude": sum(elevations) / len(elevations),
                "enhanced_max_altitude": max(elevations),
                "enhanced_min_altitude": min(elevations),
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
                # Declared TEXT in the schema, but cordelia's own Lap::insert() binds this as a
                # plain int32 (Garmin-epoch, same as -- despite the type mismatch running the
                # other way -- what Session.start_time actually is too). SQLite's TEXT-affinity
                # coercion then stores it as the integer's text digits, not an ISO 8601 string.
                # Confirmed against cordelia/src/records/lap.cpp:903 and :1426. See docs/plan.md.
                "start_time": start_garmin,
                "sport_id": SPORT_RUNNING,
            },
        )
    )

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
        "enhanced_speed",
        "Temperature",
    ]
    record_rows = [
        {
            "file_number": file_number,
            "Timestamp": cdb.to_iso8601(s["timestamp"]),
            "position_lat": cdb.degrees_to_semicircles(s["lat"]),
            "position_long": cdb.degrees_to_semicircles(s["lon"]),
            "Altitude": s["ele"],
            "heart_rate": round(s["heart_rate"]),
            "Cadence": round(s["cadence"]),
            "Distance": s["distance"],
            "Speed": s["speed"],
            "enhanced_speed": s["speed"],
            "Temperature": round(s["temperature_c"]),
        }
        for s in samples
    ]
    statements.append(cdb.insert_many_statement("Record", record_columns, record_rows))

    return statements


def generate(days: int, start_date: date, seed: int, route_path: Path, output_path: Path) -> None:
    route = Route(load_route(route_path))
    rng = random.Random(seed)

    lines = [
        "-- Synthetic Cordelia sample data generated by generate_sample_data.py.",
        f"-- {days} daily ~{route.length_m / 1000:.2f} km runs starting {start_date.isoformat()},",
        f"-- route: {route_path.name} (see data/SOURCES.md), seed={seed}.",
        "-- Apply sql/create_tables.sql to an empty database before this file.",
        "-- All data is fabricated; no real person, device, or activity is represented.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]

    for day_index in range(1, days + 1):
        run_date = start_date + timedelta(days=day_index - 1)
        run = simulate_day(rng, route, run_date)
        lines.append(f"-- Day {day_index}: {run_date.isoformat()}")
        lines.extend(build_day_statements(day_index, run))
        lines.append("")

    lines.append("COMMIT;")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=30, help="number of consecutive daily runs (default: 30)")
    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        default=None,
        help="first run's date, YYYY-MM-DD (default: today minus (days-1))",
    )
    parser.add_argument("--seed", type=int, default=970, help="random seed, for reproducible output (default: 970)")
    parser.add_argument("--route", type=Path, default=DEFAULT_ROUTE, help="GPX route file to run along")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="output .sql file path")
    args = parser.parse_args()

    start_date = args.start_date or (date.today() - timedelta(days=args.days - 1))
    generate(args.days, start_date, args.seed, args.route, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
