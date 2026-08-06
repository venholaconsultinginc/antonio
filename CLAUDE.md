# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

## What this repo is

`antonio` is a small, public set of Python example scripts ("seed" examples) showing how to query
a **Cordelia** SQLite database and produce basic report plots. It is not a maintained analytics
tool, and it does not generate its own demo data — that lives in a separate, private sibling repo,
[`data_generators`](https://github.com/venholaconsultinginc/data_generators)
(`venholaconsultinginc/data_generators`), moved out of antonio entirely on 2026-08-06 since none of
the generation machinery is customer-facing. This repo's own job is narrower and more focused:
report/plotting scripts a Cordelia user can read, copy, and run against their own database, plus
the getting-started documentation for them — see `docs/` for the illustration assets already
prepared for those future help pages (one per sport: running, biking, kayaking, strength training).

**Namesake:** Antonio, the sea captain in *Twelfth Night* who stakes Sebastian with support to get
going, then lets him make his own way — the intended relationship between this repo and its users.
It's one repo in a larger Shakespeare-named family (see the sibling `cordelia`, `goneril`, etc.
repos), but unlike the rest of that family this one is genuinely public on GitHub, not a private
Fossil repo with just a public overview page. (`data_generators`, its own newer sibling, breaks
that public pattern deliberately — it's private, and doesn't carry a Shakespeare namesake, since
it's infrastructure rather than part of the public-facing family.)

## Version control

Plain **git** on GitHub (`venholaconsultinginc/antonio`), not Fossil. This is the one *public* repo
in the family that isn't Fossil-hosted — don't apply the sibling repos' Fossil conventions here.

## Data source: Cordelia's SQLite schema

Cordelia (the sibling `../cordelia` C++ project) parses Garmin `.FIT` files into ~120 SQLite
tables, one per FIT message type. Report scripts here will need to read at least `FileID`,
`Activity`, `Event`, `DeviceInfo`, `Session`, `Lap`, and `Record` — the set a plain running/cycling
activity populates; `data_generators`' own `CLAUDE.md` has the full ten-table list (it also covers
`FileCreator`/`Sport`/`SetX`, needed for cycling/strength but not by every report).

**Before trusting any schema detail here: it hasn't been re-verified against `cordelia` recently.**
Diff against the current `CREATE TABLE` statements in `../cordelia/src/records/*.cpp` (or
`data_generators/sql/create_tables.sql`, extracted from that same source) before relying on it —
`cordelia` is under active development and this repo does not track it automatically.

Three encoding rules matter more than anything else for reading a Cordelia database correctly,
because getting them wrong produces a database that opens fine but is read as silently wrong data:

1. **GPS is semicircle-encoded**, not plain degrees: `position_lat`/`position_long` are `INTEGER`
   int32, `degrees = semicircles * 180 / 2^31`.
2. **Every timestamp-semantic column is ISO 8601 TEXT**, fixed 19-char
   `YYYY-MM-DDTHH:MM:SS` (UTC, no offset) — including `Session.start_time` and `Lap.start_time`.
   There is no Garmin-epoch-integer encoding anywhere in the tables listed above, as of cordelia
   ticket #72 (fixed 2026-08-06, fossil commit `b2a77bad4b`). Don't assume a `CREATE TABLE` type is
   a reliable guide without checking real data first — that class of drift is always possible
   elsewhere in `cordelia`'s ~120 tables.
3. `Session`/`Lap`/`Activity` each carry their own `event_id`/`event_type` pair (confirmed real
   values: `Session.event_id=8`, `Lap.event_id=9`, `Activity.event_id=26`, all `event_type=1`) —
   distinct from the `Event` table's own generic timer values (`event_id=0`, `event_type` 0/4 for
   start/stop_all). Don't confuse the two when filtering either table.

**No shared helper module exists in this repo yet.** `data_generators/cordelia_db.py` is
write-only (it only ever generates databases, never reads one back) — a report script here needs
its own, read-oriented module (`semicircles_to_degrees`, `from_iso8601`, an "open this database and
hand me a tidy DataFrame" helper), built fresh when Phase 3 actually starts. Don't import across
repos or try to share one module between the two; they solve different problems.

## Style

This is example/seed code meant to be read and copied by someone learning the schema, not a
library. Favor clarity over abstraction: prefer several similar, obvious scripts over one clever
parameterized one. Every report script should be readable top-to-bottom on its own.

## Data hygiene

This repo never contains real personal fitness data, and shouldn't need to guard against it
directly — the only databases anyone runs a report script here against are either their own real
Cordelia database (never touches this repo) or a synthetic demo database produced by
`data_generators` (fabricated, no real person represented). If you're ever tempted to add a real
`.fit`/`.sqlite` file here for testing, don't — see `data_generators`' own `CLAUDE.md` for the data
hygiene lessons learned building the generators (a geometry-only GPS extraction and a real
person's name both slipped into that repo's working state before being caught and fixed; the
standing rule there is stricter than "strip personal fields," it's "don't use a real recording at
all").

## Running

No report scripts exist yet — this section will document how to run them once Phase 3 starts.
`requirements.txt` (pandas, matplotlib) is a forward declaration for that work.

To get a demo `.sqlite` database to develop against in the meantime, see
[`data_generators`](https://github.com/venholaconsultinginc/data_generators) (private) — clone it
separately and run whichever generator matches the sport you're working on.

No test suite. Once report scripts exist, validation is running each one against a
`data_generators`-produced database and checking the plot looks sane — the specific checks belong
in this repo's own docs once there's something to check.
