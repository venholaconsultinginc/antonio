<img src="antonio-running.png" alt="" width="220" align="right">

# Running

*Skeleton page — placeholder for the running getting-started guide, not the finished thing. See
"Still to do" below for what's missing.*

## Example database

[`cordelia-sample-running.sqlite`](../example-data/cordelia-sample-running.sqlite) — 30
consecutive daily ~5&nbsp;km runs along a real public route, fabricated (no real person, device,
or activity represented). SHA-256 checksum and GPG signature ship alongside it; see the root
[README](../README.md#example-databases) for how to verify them.

```bash
sqlite3 example-data/cordelia-sample-running.sqlite
```

## What a running activity looks like in Cordelia

*TODO: short tour of the tables a running activity actually populates (`FileID`, `Activity`,
`Event`, `DeviceInfo`, `Session`, `Lap`, `Record`) and the two encoding gotchas that trip people up
first — semicircle GPS, ISO 8601 timestamps.*

## Example reports

*Not written yet — Phase 3. Planned: a pace-trend line plot across the 30 days, and a GPS route
map for a single run.*

## Using your own data

*TODO: how to point whichever report script exists at your own Cordelia database instead of the
example one.*
