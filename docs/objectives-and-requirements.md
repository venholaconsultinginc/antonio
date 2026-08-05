# Objectives and Requirements

## Purpose

`antonio` is a small, public collection of Python example scripts that show how to run basic
reports and plots against a **Cordelia** SQLite database. Cordelia (see the sibling `cordelia`
project) reads Garmin `.FIT` activity files and persists every parsed record to SQLite. This repo
is the "seed" layer on top of that: enough working example code that a user comfortable with
Python can see the shape of the data and start writing their own reports, without having to
reverse-engineer the schema from scratch.

The namesake follows the family's Shakespeare convention: Antonio, the sea captain in *Twelfth
Night*, stakes Sebastian with money and support to get him going, then steps back so Sebastian
makes his own way. That's the intended relationship between this repo and its users — a seed, not
a dependency.

## Audience

Cordelia users who are comfortable with Python and want to explore or report on their own
Cordelia database. Not aimed at non-programmers, and not a supported analytics product — issues
and PRs are welcome but there's no maintenance SLA.

## Objectives

1. **Primary** — provide a handful of minimal, readable Python scripts that each produce one basic
   plot from a Cordelia SQLite database (e.g. pace trend, a single run's route, daily distance),
   demonstrating the query patterns and unit conversions the schema requires.
2. **Secondary** — ship a synthetic sample-data generator that builds a schema-compatible SQLite
   database (30 days of one ~5 km run per day, varying pace, a repeating GPS loop) so the examples
   are runnable immediately, without a real Cordelia export and without any real personal data.

## Non-goals

Explicit boundaries, so scope doesn't creep past "seed examples":

- Not a full analytics tool, dashboard, or web app.
- Not a substitute for Cordelia's own JSON/CSV/XLSX export features.
- Not guaranteed to track every future change to Cordelia's schema — this is example code, not a
  maintained integration. See "Schema drift" in `plan.md` for how this is mitigated instead.
- No writes back to a real Cordelia database — read-only queries against the DB file.
- No networking, cloud sync, or credentials of any kind.
- No real personal fitness data anywhere in the repo, its history, or its issues — synthetic data
  only.

## Functional requirements

| # | Requirement |
|---|-------------|
| FR1 | A generator script produces a Cordelia-schema-compatible SQLite file: 30 consecutive daily activities, each ~5 km, varying pace, one repeating GPS loop route, at a realistic per-second `Record` sample rate. |
| FR2 | A small shared helper module opens a Cordelia SQLite DB and converts its native encodings — semicircle GPS integers, Garmin-epoch integers, fixed-format ISO 8601 timestamp text — into plain Python/pandas types. Every report script uses it rather than re-deriving the conversions. |
| FR3 | At least three basic report scripts, each independently runnable and each producing one plot: a pace-over-time trend across the 30 days, a single run's GPS route, and a daily distance/duration summary. |
| FR4 | `README.md` documents environment setup, how to generate the sample database, and how to run each report script. |

## Non-functional requirements

| # | Requirement |
|---|-------------|
| NFR1 | Runs from a plain `pip install -r requirements.txt` — pandas + matplotlib class of dependencies only, nothing exotic. |
| NFR2 | Each script is readable top-to-bottom by someone with basic Python/pandas experience. Favor clarity over abstraction — this is example code meant to be read and copied, not a library. |
| NFR3 | No credentials, secrets, or real personal data anywhere in the repo, ever — enforced by using only the synthetic generator's output as example data. |
| NFR4 | The schema baked into the helper module and generator is dated and traceable to a specific point in the `cordelia` source, so staleness is visible rather than silent. |

## Data source

Cordelia persists one row per parsed FIT message type across roughly 120 tables. Only a handful
matter for this repo's purpose — the ones a single running activity actually populates:
`FileID`, `Activity`, `Event`, `DeviceInfo`, `Session`, `Lap`, `Record`. Full technical detail
(exact encodings, constraints, and where each was confirmed in the `cordelia` source) is in
`plan.md`.
