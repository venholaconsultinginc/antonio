<img src="antonio-biking.png" alt="" width="220" align="right">

# Cycling

*Skeleton page — placeholder for the cycling getting-started guide, not the finished thing. See
"Still to do" below for what's missing.*

New to Python, or don't have dependencies installed yet? See [setup.md](setup.md) first.

## Example database

4 rides along the real Tour de Victoria 80&nbsp;km road-cycling route, fabricated (no real person,
device, or activity represented). Download `cordelia-sample-cycling.sqlite`, with its SHA-256
checksum and GPG signature, from [downloads.md](downloads.md).

```bash
sqlite3 example-data/cordelia-sample-cycling.sqlite
```

## What a cycling activity looks like in Cordelia

*TODO: short tour of the tables a cycling activity populates (the running set plus `FileCreator`
and `Sport`) and what's different from running (e.g. `enhanced_speed` vs. legacy `Speed`).*

## Example reports

*Not written yet — Phase 3. Planned: a pace-trend line plot across the 4 rides, and a GPS route
map.*

## Using your own data

*TODO: how to point whichever report script exists at your own Cordelia database instead of the
example one.*
