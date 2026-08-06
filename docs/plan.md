# Plan

Companion to `objectives-and-requirements.md` — that document says *what* and *why*; this one says
*how*, in phases, plus the technical detail needed to implement each phase correctly the first
time.

## Schema snapshot

Captured from the `cordelia` source (sibling repo, private Fossil project) on **2026-08-05**. If
Cordelia's schema changes after this date, this repo's generator and helper module will not
automatically follow — see "Schema drift" under Risks.

One imported `.FIT` file = one row in `FileID`, whose autoincrement primary key becomes
`file_number` — the foreign key stamped onto every other row belonging to that activity
(`src/scanner/fit_scanner.cpp:141-167` in `cordelia`). For 30 daily runs, the generator produces
30 independent `file_number`s, exactly as if 30 separate `.FIT` files had been imported.

Minimal table set for one running activity, in insert order:

| Table | Role | Notes |
|---|---|---|
| `FileID` | One row per "file"/activity | `UNIQUE(serial_number, time_created)`; `path`, `imported_at` are `NOT NULL`. |
| `Activity` | Activity-level metadata | One row per file. |
| `Event` | Start/stop timer events | Minimal: timer start + stop per activity. |
| `DeviceInfo` | Recording device metadata | One row is enough (a single watch). |
| `Session` | Activity summary (~150 columns) | Only a handful matter: `sport_id`, `total_distance`, `avg_speed`, `max_speed`, `start_time`, `total_elapsed_time`. Rest can be 0/NULL. |
| `Lap` | Lap summary (~100+ columns) | One lap per activity is enough for a basic 5 km run; same "only a few columns matter" story as `Session`. |
| `Record` | Per-sample trackpoint (~85 columns) | One row per GPS/HR/speed sample. Only `Timestamp`, `position_lat/long`, `Altitude`, `heart_rate`, `Cadence`, `Distance`, `Speed`, `enhanced_speed` matter; rest 0/NULL. |

### Encodings that must be handled correctly

These are the parts most likely to produce a database that *looks* right but silently isn't:

1. **GPS is semicircle-encoded.** `position_lat`/`position_long` in `Record` are `INTEGER`
   (int32), not plain degrees: `semicircles = round(degrees * 2^31 / 180)`. Documented across
   several `cordelia` record types' `.ixx` files (`record.ixx`, `session.ixx`, `lap.ixx`, etc.).
2. **All timestamp-semantic columns are ISO 8601 TEXT.** Fixed 19-character
   `YYYY-MM-DDTHH:MM:SS`, UTC, no offset — `ISO8601DateTime::try_from_string`
   (`cordelia/src/core/iso8601_datetime.cpp:40-54`) validates the exact length and separator
   positions and will reject anything else. This wasn't always true: `Session.start_time` was
   declared `INTEGER` while actually storing ISO 8601 text, and `Lap.start_time` was declared
   `TEXT` while actually storing a raw Garmin-epoch integer — two schema/implementation
   mismatches discovered while building this repo (see `cordelia`'s ticket #72). Both were fixed
   2026-08-06 (fossil commit `b2a77bad4b`), which standardized every timestamp-semantic column
   across the whole schema — including several outside the tables this repo tracks
   (`Activity.local_timestamp`, `Monitoring*`, `TimestampCorrelation`) — on `ISO8601DateTime`/
   `TEXT`. There is no more Garmin-epoch-integer encoding anywhere in the tables this repo
   touches; `cordelia_db.py`'s Garmin-epoch conversion functions were retired along with it.
   The lesson for future schema work here remains: check the actual bind/extract call, or real
   data, per column — a declared `CREATE TABLE` type was not a reliable guide before this fix,
   and a repeat of the same class of drift elsewhere in `cordelia`'s ~120 tables is always
   possible.
3. **`FileID` uniqueness.** `UNIQUE(serial_number, time_created)` means each of the 30 days needs a
   distinct `time_created`, which falls out naturally from generating one activity per calendar
   day.
4. **Each message type has its own `event_id`/`event_type` pair recording which kind of FIT
   message closed it out — not a single shared "timer event" value.** The `Event` table's own
   timer start/stop rows do use `event_id=0` (timer), `event_type` 0/4 (start/stop_all) — that
   part was right. But `Session`, `Lap`, and `Activity` each carry their *own* `event_id`/
   `event_type` columns for a different purpose, confirmed against real data: `Session.event_id=8`,
   `Lap.event_id=9`, `Activity.event_id=26`, all with `event_type=1`. Reusing the `Event` table's
   timer constants for these (as this repo's generator originally did) is wrong.

The shared helper module (`cordelia_db.py`, Phase 1) is where both conversions live, so every
report script gets them for free instead of re-deriving them.

## Phases

### Phase 0 — Foundations (this step)

- `docs/objectives-and-requirements.md`, `docs/plan.md` (this file), `CLAUDE.md`.
- `requirements.txt` skeleton (pandas, matplotlib).

### Phase 1 — Shared DB helper module (done, 2026-08-05)

- `cordelia_db.py`: semicircle ↔ decimal-degrees, ISO 8601 TEXT formatting, and `INSERT`
  statement building (`sql/create_tables.sql` holds the `CREATE TABLE` statements themselves,
  extracted verbatim from `cordelia`, rather than duplicating them here). Originally also carried
  Garmin-epoch ↔ Unix time conversions for `Lap.start_time`; retired 2026-08-06 once cordelia
  ticket #72's fix made every timestamp-semantic column uniformly ISO 8601 TEXT (see the
  encoding-rules section above) and that conversion had nothing left to do.
- A round-trip self-check runs at import time (GPS conversion, timestamp format, column-list
  parsing, and that `Session`/`Lap.start_time` are still declared `TEXT`) so a conversion bug or
  schema regression fails loudly on import instead of producing a plausible-looking wrong map.
  Note: this phase originally scoped only *reading* a live SQLite file; what actually got built
  first is the write-side (INSERT-building) half, since Phase 2 needed it immediately and Phase 3
  (which needs the read side) hasn't started. The two live in the same module by design — see the
  module docstring.
- **Revised 2026-08-06**: the write side no longer builds SQL text. `insert_statement`/
  `insert_many_statement`/`sql_literal` are replaced by `create_schema`/`insert_row`/`insert_many`,
  which execute directly against a live `sqlite3.Connection`. The motivating fix: `insert_row`
  returns the row's real assigned primary key (`cursor.lastrowid`) and refuses to insert if the
  caller tries to set that primary key explicitly — closing off exactly the bug described in the
  Phase 2 correction below, where a generator's own counter had to be trusted to match what SQLite
  would later assign.

### Phase 2 — Synthetic data generator (done, 2026-08-05)

- `generate_sample_data.py`, CLI-driven: output path, number of days (default 30), random seed
  (default 970, for reproducible example output), start date (default: 2026-08-01 as of
  2026-08-06 -- originally "today minus (days-1)", changed to a fixed date so re-running the
  generator on a different day doesn't shift the output, matching the bike generator's fixed
  `DEFAULT_RIDE_DATES`).
- Route: `data/route_running.gpx`, a real public route named "5K Run for the Cure" in Ottawa (CIBC Run for
  the Cure, a Canadian Cancer Society charity run) — see `data/SOURCES.md` for provenance. ~5.03 km,
  48 waypoints with elevation, walked once per simulated run at 1 Hz for `Record` rows.
- Pace, heart rate, cadence, and temperature each get one uniform +/-10% multiplier per day off a
  fixed baseline (5:45 min/km, 150 bpm, 85 spm, 20°C), plus light per-sample noise so within-run
  values aren't flat. Start time is ~9am +/-10% (of 540 minutes past midnight). Device is a
  fabricated Garmin Forerunner 970 — real serial number and Garmin `garmin_product` code weren't
  used: no authoritative public source for the 970's FIT product code was found, so a clearly
  synthetic placeholder is used instead (see `generate_sample_data.py`'s constants).
- Output is plain SQL `INSERT` statements (`output/sample_data.sql`), not a live SQLite write —
  batched multi-row inserts for `Record` and only-the-populated-columns for every table, both
  needed to keep output size sane (an earlier one-`INSERT`-per-row, every-column version of this
  ran to 101 MB for 30 days; the current version is ~5 MB).
- Writes `FileID` → `Activity`, `Event`, `DeviceInfo`, `Session`, `Lap`, `Record` for each of the
  30 days, using `cordelia_db.py`'s conversions throughout.
- **Corrected 2026-08-05** (same day, after cross-checking against a real Cordelia-produced
  database while building Phase 2b below): `Session.start_time` was wrongly written as a
  Garmin-epoch integer — it's actually ISO 8601 TEXT — and `Session`/`Lap`/`Activity`'s own
  `event_id`/`event_type` fields wrongly reused the `Event` table's generic timer constants
  instead of their real per-message values (8/9/26, `event_type=1`). See the encoding-rules
  section above; regenerated and re-pushed before Phase 2b started.
- **Revised 2026-08-06**: output is now a real SQLite database (`output/sample_data.sqlite`),
  written directly via `cordelia_db.py`'s `insert_row`/`insert_many` (see Phase 1's revision note)
  — no more `output/sample_data.sql` text file, no separate `sqlite3 ... <` load step. This also
  fixed a latent correctness risk: the generator previously self-assigned `file_number` as a plain
  Python counter and wrote it as a literal into every dependent table's row, which was only correct
  because it assumed SQLite's `AUTOINCREMENT` would assign those exact same values, in that exact
  order, once the text was later loaded into a fresh table — an assumption that held in practice
  but was never actually verified. Every dependent row now uses the real `file_number` `insert_row`
  reads back from the `FileID` insert itself.

### Phase 2b — Cycling generator (done, 2026-08-05)

- `generate_sample_data_bike.py`, built on Phase 2's `Route`/`load_route` (imported, not
  duplicated). CLI-driven: ride dates (default 2026-09-05/12/18/26), seed (default 1040), route,
  output path.
- Route: `data/route_bike.gpx`, the real official "2026 Tour de Victoria 80km" road-cycling route
  (organizer-published GPX, not reconstructed from an API response like the running route was) —
  see `data/SOURCES.md`. ~77 km, 1832 waypoints with elevation.
- Unlike Phase 2, whose baselines were invented, this phase's pace/heart-rate baselines (6.15 m/s,
  155 bpm) and its device/schema population fidelity come directly from a real reference ride —
  a real `.fit` file and its real Cordelia-imported `.sqlite`, provided locally for this purpose
  and never committed (see `data/SOURCES.md`'s "Real reference files" section and `CLAUDE.md`'s
  data hygiene rule). That reference revealed several real-world facts a synthetic-only approach
  couldn't have gotten right by guessing:
  - Real Garmin `garmin_product` codes: Edge 1040 = 3843, Venu 4 = 3865 (no placeholder needed,
    unlike Phase 2's Forerunner 970).
  - `sport_id=2`, `sub_sport_id=7`, `sport_profile_name="ROAD"` for road cycling — confirmed, not
    guessed.
  - A real Edge 1040 + paired Venu 4 (for heart rate) produces **four** `DeviceInfo` rows per
    file: the Edge itself, an internal Edge sub-device, the Venu 4's own identity, and the Venu
    4's ANT+ heart-rate broadcast to the Edge (generic `garmin_product_id=255`,
    `antplus_device_type=120`) — not one row per physical device as Phase 2 assumed.
  - A real Edge 1040 (no power meter or cadence sensor paired) writes `Power`, `Cadence`, and
    `gps_accuracy` as explicit `0` for every `Record` row, and the same explicit-`0` pattern
    (not `NULL`) for `DeviceInfo`'s battery fields on devices that don't report battery. It
    populates only `enhanced_speed`/`enhanced_altitude`, never the legacy `Speed`/`Altitude`
    fields (also explicit `0`, not `enhanced_speed`/`Speed` both carrying the real value the way
    Phase 2 does). `Session`/`Lap` don't carry any altitude summary fields at all in this real
    data (only `total_ascent`/`total_descent`) — also not replicated by Phase 2's design.
  - This generator matches all of the above exactly. Two secondary realism details were
    deliberately **not** replicated, per an explicit "keep it simple" decision: the real ride's 6
    auto-pause start/stop `Event` pairs (one pair used instead, as in Phase 2) and its mid-ride
    `DeviceInfo` refresh duplicating all 4 rows a second time (one set used instead). Also not
    replicated: real auto-lap-every-5km (`lap_trigger=2`, 8 laps on the reference ride) — one lap
    per ride instead, `lap_trigger=7` (session-end), consistent with Phase 2's "one lap is enough"
    design.
  - `total_training_effect`, `total_anaerobic_training_effect`, `avg_vam`, and
    `training_load_peak` are Garmin's own derived/computed metrics, not directly-measured data —
    left unset rather than faked.
  - Temperature baseline (15°C) is **not** from the reference ride (a warm August afternoon); it's
    an invented September-Victoria-morning assumption, same status as Phase 2's baselines.
- `FileCreator` and `Sport` tables added to `sql/create_tables.sql` and populated — real data
  showed both populated for a real ride; Phase 2 didn't include them.
- Same output approach as Phase 2: batched `INSERT`s, only-populated-columns elsewhere, ~5.2 MB
  for 4 rides (~49,000 `Record` rows).
- **Revised 2026-08-06**: same direct-to-`.sqlite` rework as Phase 2 above, output is now
  `output/sample_data_bike.sqlite`.

### Phase 2c — Kayaking generator (done, 2026-08-06)

- `generate_sample_data_kayak.py`, built on Phase 2's `Route`/`load_route` (imported, not
  duplicated). CLI-driven: eight fixed September 2026 paddle dates (2026-09-04/06/11/13/18/20/26/27,
  set by the user rather than left relative-to-today, same reasoning as Phase 2's start-date
  revision below), seed (default 41), route, output path. Direct-to-`.sqlite` from the start —
  built after the Phase 1/2/2b revisions above, so it never had a `.sql`-text phase to move away
  from.
- Route: `data/route_kayak.gpx`, a real out-and-back paddle route off Mayne Island, BC — unlike
  Phase 2/2b's routes (a public map page, an event organizer's own GPX), this one's geometry was
  extracted from the user's own real personal recording, with explicit owner confirmation that the
  public-beach launch/return point and the geometry-only extraction were both fine to commit. See
  `data/SOURCES.md`'s `route_kayak.gpx` and "Real reference files" sections for exactly what was
  and wasn't taken, and `CLAUDE.md`'s data hygiene section for the one-exception framing.
- Pace/heart-rate/cadence baselines (1.056 m/s, 121 bpm, 22 strokes/min) come directly from the
  real reference paddle's `Session` summary, same "ground-truthed, not invented" approach as
  Phase 2b. Device is a real Garmin Venu (`garmin_product_id=3226`) — real model, fabricated
  serial, same pattern as Phase 2b's Edge 1040/Venu 4.
- **Sport code deliberately does not match the reference**: the real paddle was recorded as
  `sport_id=15` (Rowing)/"Row" (plausible — many Garmin watches lack a distinct kayak profile) —
  but since this repo's data is explicitly meant to demonstrate kayaking, `sport_id=41` (FIT's
  actual Kayaking code) is used instead, a conscious exception to Phase 2b's "confirmed against
  real data, not guessed" philosophy for this one field only.
- **Wind, simulated as a pace/heart-rate effect, not a stored field**: checked every table in the
  real reference database (not just the nine this repo normally touches) — there is no
  wind/weather column anywhere in Cordelia's schema. Each simulated paddle draws one signed daily
  wind strength; since the route is out-and-back, a single value naturally gives a tailwind on one
  leg and a headwind on the other — speed shifts with it, heart rate shifts the opposite way
  (harder effort against the wind for less boat speed). Purely a simulation input shaping the
  numbers, the same status Temperature already had in Phase 2/2b — never written to any column of
  its own.
- Real device reports no elevation at all for this activity (`Altitude`/`enhanced_altitude` flat
  `0` for all 5610 real `Record` rows) — carried through as explicit `0`, not invented, same
  explicit-not-`NULL` precedent as Phase 2b's unequipped-sensor fields. Temperature *is* invented
  (17°C, a plausible September-Mayne-Island-morning assumption), since the real device reported
  flat `0` there too (not measured, not zero weather).
- Two `DeviceInfo` rows only (the Venu and its own internal sub-device) — the real reference logged
  six more rows for unidentified/no-vendor ANT accessories, not replicated, same "keep it simple"
  simplification Phase 2b already makes for its own reference's messier details. One lap per
  paddle (`lap_trigger=7`, session-end), not the real reference's auto-lap-every-500m — same
  simplification as Phase 2/2b.

### Phase 3 — Report scripts

Each is a standalone, runnable script — no shared CLI framework, since the point is that a reader
can open one file and see the whole thing:

- `pace_trend.py` — average pace per day across the 30-day window, line plot.
- `route_map.py` — GPS trace for a single run, one plot.
- `daily_summary.py` — distance and duration per day, bar plot.

### Phase 4 — Documentation and polish

- `README.md`: environment setup, `pip install -r requirements.txt`, how to run the generator,
  how to run each report script, and what output to expect.
- Pin dependency versions in `requirements.txt` once the scripts are working.

### Phase 5 — Validation

- Run the full pipeline end to end: generate → each report script → confirm plots look sane
  (route is a closed loop, pace varies but stays in-band, distances land near 5 km/day).
- Re-check the generator's `CREATE TABLE` statements against current `cordelia` source before
  publishing, since Phase 0's snapshot date may have drifted by the time this phase runs.
- Scan for secrets/PII before every push (this should never trigger, given NFR3, but is a cheap
  final check).

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| **Schema drift** — `cordelia` is under active development; a hand-copied schema goes stale silently. | Date-stamp the schema snapshot (see above); re-verify against `cordelia` source immediately before any release, not just at initial writing. |
| **Encoding bugs** (semicircle math, epoch offset, timestamp format) are easy to get subtly wrong and produce a database that opens fine but plots garbage. | Centralize all conversions in `cordelia_db.py` (Phase 1) with a self-check, rather than reimplementing per script. |
| **Accidental real data** — a real Cordelia export ending up committed. | Only ever commit the synthetic generator's code, never its output `.db` file; add the generated database path to `.gitignore` before Phase 2 lands. |
| **Scope creep** — "seed examples" drifting into a maintained reporting tool. | `objectives-and-requirements.md`'s Non-goals section is the anchor; new feature requests get checked against it before being added. |
| **Public repo, private schema source** — unlike `cordelia`'s own private Fossil hosting, `antonio` is public on GitHub. | Nothing in the schema itself is sensitive (it's the user's own project), but no real data, credentials, or internal-only URLs should ever appear here — this is the one repo in the family where that matters. |

## Rough effort

Consistent with the original estimate: Phase 1–3 (the actual code) is roughly a half-day to a day
of focused work now that the schema detail above is already extracted; Phase 0 and 4 are
lightweight; Phase 5 is a final pass, not new work.
