# Repository layout: a customer-first reorganization

**Status: draft — structure decided 2026-08-06, Julia scope still open, not yet implemented.**

## The problem

Right now this repo is organized around how it was *built*, not how it will be *used*. A visitor
landing here today sees, at the root: two synthetic-data generators, a schema-extraction SQL file,
and a `CLAUDE.md`/`docs/plan.md` full of Fossil ticket cross-references and bug-hunting narrative.
There is no report/plotting code yet (Phase 3), so there is currently nothing at all for the
actual target reader to run against their own data.

That target reader is not us, and isn't interested in how we tested this:

> A technical/data-science person — proficient in Python (maybe R or Julia) — who found Cordelia
> on the website, has already imported their own `.fit` files into a real Cordelia database, found
> a link to this repo, and wants to plot their own data *quickly*. They don't care how the seed
> data was generated, what bugs were found along the way, or which Fossil ticket fixed what.

Everything below is organized around serving that person first, with everything else demoted to
clearly-labeled secondary status — not deleted, since it's still useful and builds trust (a
customer can see exactly how the demo data was made if they want to), just no longer competing for
attention with the thing they actually came for.

## Decided (2026-08-06)

1. **Demo databases and the schema reference live on the website, not in antonio.** The Cordelia
   home at `https://www.venholaconsulting.ca` already carries a data dictionary stub — see
   `../website/src/apps/help/en/cordelia/data-dictionary.html` (overview) and
   `data-dictionary-detail.html` (intended full field reference, currently thin). The
   encoding-gotcha writeup accumulated in this repo's `docs/plan.md` (semicircle GPS, ISO 8601
   timestamps, `FileID` uniqueness, per-table `event_id` semantics) should migrate there as the
   authoritative version, not stay duplicated in antonio. Downloadable demo `.sqlite` files (see
   #3) belong on that same site — `website` is a separate, Fossil-hosted repo
   (`~/Repositories/website`), deployed via its own `scripts/deploy.sh`; migrating content there
   and wiring up file hosting is a `website`-repo task, not an antonio one, and should be tracked
   there when it's picked up.
2. **Julia is reporting-only — never data generation.** All demo-data generation (running, biking,
   and the future kayak/strength generators) stays Python, permanently; `example_reporting/julia/`
   only ever reads an existing Cordelia `.sqlite` (demo or real) and reports off it. This narrows
   `CordeliaDB.jl` to the read direction alone — no `insert_statement`, no `degrees_to_semicircles`,
   no write path at all — so there's no risk of a Julia-side generator drifting from the Python
   ones, and less surface to keep in sync than a naive "port cordelia_db.py" would suggest.
3. **Python stays the primary reporting language; Julia is a scoped secondary set, not full
   parity.** `docs/objectives-and-requirements.md` (the charter doc) defines antonio's audience as
   "comfortable with Python" and frames every FR/NFR around Python — considered and explicitly
   rejected flipping that to Julia-primary (2026-08-06), so the charter doc is not being touched.
   Concretely: Python's `example_reporting/python/` gets the complete example set; Julia's
   `example_reporting/julia/` gets the flagship slice from the "Julia assessment" section below
   (`pace_trend` + `CordeliaDB.jl`), expanded later only if real interest justifies it.
4. **Demo data ships as downloadable `.sqlite` databases in real Cordelia structure, written
   directly — no intermediate `.sql` text file at all** (revised 2026-08-06, replacing the earlier
   "generate `.sql`, then assemble" framing below). A generator opens a Python `sqlite3` connection,
   executes `create_tables.sql` via `executescript()`, then inserts rows straight through that
   connection instead of building INSERT statements as strings for something else to load later.
   This isn't just a shorter pipeline — it removes a real correctness risk. Today's generators
   self-assign `file_number` as a plain Python counter (1, 2, 3…) and write it as a literal into
   every dependent table's (`Activity`, `Session`, `Lap`, `Record`, etc.) generated SQL text, which
   is only correct because it *assumes* SQLite's `AUTOINCREMENT` will assign those exact same
   values, in that exact order, when the text is later executed against a fresh table — an
   implicit, unenforced assumption. Writing directly through a live connection instead lets each
   `FileID` insert hand back its real assigned primary key (`cursor.lastrowid`, or
   `INSERT ... RETURNING file_number` — the same pattern cordelia's own C++ already uses for
   `SetX.RecordNumber`, see `set_x.cpp`), and every dependent row uses that real value directly. No
   parallel counter to keep in sync. This reasoning applies equally to the *existing* running/bike
   generators, not just new ones — reworking them to match is follow-on implementation work, not
   done in this planning pass. Per this repo's data-hygiene rule, no `.db`/`.sqlite` file is ever
   committed to antonio's git history; the built files are upload artifacts for the website, not
   repo contents.
5. **Directory split: `example_reporting/python/` and `example_reporting/julia/`.** Replaces the
   earlier flat `examples/` idea now that two languages are on the table.

## The bigger goal: four or five demo databases, one per sport

Not just running and cycling — the target set is **running, biking, kayaking, strength training,
and more to come.** Checked against `cordelia`'s actual FIT support before assuming feasibility:

- **Kayaking** (`FIT_SPORT_KAYAKING`, `FIT_SUB_SPORT_WHITEWATER`) is GPS/`Record`-based like
  running and biking — structurally the same shape of generator, needs its own real-route GPX
  source under `demo-data/data/` (see `route_running.gpx`/`route_bike.gpx` and `SOURCES.md` for
  the pattern: real public route geometry only, no real athlete data).
- **Strength training** (`FIT_SUB_SPORT_STRENGTH_TRAINING`) is a genuinely different shape:
  cordelia stores it via the `SetX` table (`Repetitions`, `Weight`, `set_type`, `Category`,
  `category_subtype`, `Duration`, `start_time` — see `../cordelia/src/records/set_x.cpp`), not
  `Record`. No GPS, no continuous timeseries. This is not a copy of the running/bike generator with
  new numbers — it needs its own data model and probably its own report examples (Phase 3 side)
  since "route map" and "pace trend" don't apply. Budget it as new design work, not a template fill.

## Proposed structure

```
antonio/
├── README.md                    -- rewritten: "what is this" + quickstart, ~30 seconds to first plot
├── LICENSE
├── requirements.txt
├── antonio.svg
├── cordelia_db.py                -- shared encoding helpers (see "cordelia_db.py" note below)
├── example_reporting/
│   ├── python/
│   │   ├── pace_trend.py
│   │   ├── route_map.py
│   │   ├── weekly_summary.py
│   │   └── README.md             -- one paragraph: "each takes --db PATH; point it at your own database"
│   └── julia/                    -- scope pending: flagship example(s) + CordeliaDB.jl, not full parity yet
│       ├── CordeliaDB.jl
│       ├── pace_trend.jl
│       └── README.md
├── docs/
│   ├── getting-started.md        -- full customer walkthrough (installs, running examples, troubleshooting)
│   └── dev/                      -- clearly-labeled maintainer docs, not customer-facing
│       ├── objectives-and-requirements.md   (moved, reframed)
│       ├── plan.md                          (moved, reframed; encoding detail migrates onward to the website)
│       └── repository-layout-plan.md        (this file, once decided)
└── demo-data/                    -- clearly secondary: "no data of your own yet? start here"
    ├── generate_sample_data.py        (running — write path to rework, see "Decided" #4)
    ├── generate_sample_data_bike.py   (cycling — write path to rework, see "Decided" #4)
    ├── generate_sample_data_kayak.py  (new — TODO, writes .sqlite directly from the start)
    ├── generate_sample_data_strength.py  (new — TODO, different data model, see above)
    ├── data/                      (route_running.gpx, route_bike.gpx, route_kayak.gpx [new], SOURCES.md)
    ├── sql/create_tables.sql
    └── README.md                  -- "generates a synthetic database to practice on"
```

`CLAUDE.md` stays at root (that's a Claude Code convention, not customer-facing by definition) but
gets a short pointer at the top distinguishing the customer-facing directories from the internal
ones, so a future session — human or Claude — doesn't re-blur the line this reorganization draws.

## Why `sql/create_tables.sql` moves too

It's easy to assume this belongs at the top level since it's "the schema" — but a real customer's
real database was already built by Cordelia itself; they never run a `CREATE TABLE` statement
themselves. Its only actual consumers are the demo-data generators. It belongs with them.

## Julia assessment

Recommendation: **a scoped slice, not full parity, at least to start.**

In favor: `SQLite.jl` and `DataFrames.jl` are mature and map cleanly onto the same
query-then-tidy-DataFrame pattern the Python side needs anyway; the audience genuinely overlaps
(technical/scientific users comfortable with SQL and dataframes skew Julia-friendly); and
architecturally now is the right time, since no Phase 3 code exists yet to retrofit.

Against full parity from day one: route maps are the weak point — Python's basemap tooling
(contextily, cartopy) is plug-and-play, Julia's (Tyler.jl + GeoMakie) is newer and more setup for
what's supposed to be an obvious copy-and-run script. Julia's package precompilation also makes a
cold first run noticeably slower than Python's, which is a bad first impression for a script a
stranger downloads and runs once — fixable with a sysimage, but that's more machinery than this
repo's "clarity over cleverness" style wants to carry. And every encoding rule (semicircle GPS,
ISO 8601, `event_id` semantics) needs a second faithful, kept-in-sync implementation
(`CordeliaDB.jl`) as `cordelia`'s schema drifts — real ongoing cost, not a one-time port.

Proposal: build one flagship example — `pace_trend`, since it sidesteps the basemap problem — plus
`CordeliaDB.jl`, gauge the actual friction (time-to-first-plot, ecosystem gaps) against real use,
and expand based on interest rather than mirroring the Python set 1:1 up front. Python stays the
complete reference implementation, matching the objectives doc's stated primary audience.

## `cordelia_db.py` / `CordeliaDB.jl`: a read/write split is coming, not yet resolved

Worth flagging now rather than after Phase 3 is built: `cordelia_db.py` today is entirely
*write*-oriented (`insert_statement`, `insert_many_statement`, `sql_literal`, `degrees_to_semicircles`)
because it only ever served the demo-data generators. A real report script reading a real database
needs the *reverse* direction too — `semicircles_to_degrees` already exists, but there's no
`from_iso8601` yet, and no "open this database and hand me a tidy DataFrame" helper. Phase 3 should
settle this rather than antonio inventing two competing conventions.

The write side is also changing shape per "Decided" #4 above: `insert_statement`/
`insert_many_statement`/`sql_literal` currently render SQL as strings for something else to load
later (originally the `sqlite3` CLI); moving to direct-to-`.sqlite` generation means these become
(or are replaced by) helpers that execute parameterized statements against a live connection and
return the real assigned primary key, rather than string builders. Worth designing alongside the
read-direction helpers rather than as an afterthought, since both are `cordelia_db.py` API changes.

`CordeliaDB.jl`, if Julia proceeds, needs *only* that reverse direction — `example_reporting/julia`
never writes a database, so there's no Julia equivalent of `insert_statement`/
`degrees_to_semicircles` to build or maintain at all. The two modules aren't mirrors of each other;
`cordelia_db.py` is read+write (generation and, eventually, Python reporting), `CordeliaDB.jl` is
read-only. Smaller surface than the earlier "second faithful implementation" framing implied — the
encoding rules it still has to get right independently (semicircle decode, ISO 8601 parse) are the
same drift risk either way, just a shorter list of functions.

## Still open

1. **`website` repo work**: migrating the encoding-gotcha content into
   `data-dictionary-detail.html`, and standing up hosting for the downloadable `.sqlite` files, are
   real tasks but live in `~/Repositories/website`, a separate Fossil-hosted repo — worth its own
   session/ticket rather than folding into antonio's git history.
2. **Kayak route source**: needs a real, publicly-sourced GPX track (same sourcing standard as
   `route_running.gpx`/`route_bike.gpx` — real geometry, no real athlete data) before that
   generator can be built.
3. **Strength training data model**: needs actual design work (what a synthetic workout looks like
   in `SetX` terms — exercises, sets, reps, weight progression) before it's a generator at all;
   flagged above, not yet scoped in detail.

## What this does *not* do

This plan doesn't write the Phase 3 report scripts themselves, the new generators, or any Julia
code — it's purely about where things live and what's been decided, so that when that work does
land, it lands in the right place the first time instead of needing a second reorganization.
