# Example databases at a glance

Six pre-built, fabricated Cordelia databases ship in [`example-data/`](../example-data/): one per
sport, plus a schema-only empty one. Getting started needs no Garmin device, no Cordelia install
and no data of your own.

Each database is also published as a `.kent` archive: the same contents as newline-delimited JSON
inside a zip, written by [Kent](https://www.venholaconsulting.ca/apps/help/en/kent/archive.html).
Read one with any zip tool and a JSON parser, with neither Cordelia nor Kent installed. The
`.sqlite` file is the original; the archive is a copy of its contents. Take each table's file name
from `manifest.json`, never from the entry names: table files are numbered, `tables/00000001.jsonl`
and so on, because a table name can hold characters a file name cannot.

These were produced once, with Kent 1.4.0, and the same bytes are served from the
website. They are not reproducible: the manifest carries an export timestamp, so running
`kent archive` again gives a different file with a different checksum.

| | Sport | Contents | File | Archive |
|---|---|---|---|---|
| <img src="icon-running.svg" width="56" alt=""> | Running | 25 daily ~5&nbsp;km runs along a real public route, Sundays rested<br>Aug 1–29, 2026 · Ottawa River Pathway, Ottawa ON<br>Avg 29.2 min · 5.8 min/km pace | [`cordelia-sample-running.sqlite`](../example-data/cordelia-sample-running.sqlite) | [`.kent`](../example-data/cordelia-sample-running.kent) |
| <img src="icon-cycling.svg" width="56" alt=""> | Cycling | 4 rides along the real Tour de Victoria 80&nbsp;km road-cycling route<br>Sep 5–26, 2026 · Victoria, BC<br>Avg 204.5 min (~3h25m) · 22.6 km/h avg speed | [`cordelia-sample-cycling.sqlite`](../example-data/cordelia-sample-cycling.sqlite) | [`.kent`](../example-data/cordelia-sample-cycling.kent) |
| <img src="icon-kayaking.svg" width="56" alt=""> | Kayaking | 8 out-and-back paddles in the Gulf Islands<br>Sep 4–27, 2026 · Mayne Island, BC<br>Avg 91.6 min (~1h32m) · 45.7&nbsp;km total (~5.7&nbsp;km/paddle) | [`cordelia-sample-kayaking.sqlite`](../example-data/cordelia-sample-kayaking.sqlite) | [`.kent`](../example-data/cordelia-sample-kayaking.kent) |
| <img src="icon-strength-training.svg" width="56" alt=""> | Strength training | 8 sessions of work sets and rest periods; no GPS, so no distance or speed<br>Sep 1–24, 2026 · indoor (no GPS)<br>Avg 51.3 min · 51 work sets + 50 rest periods/session | [`cordelia-sample-strength-training.sqlite`](../example-data/cordelia-sample-strength-training.sqlite) | [`.kent`](../example-data/cordelia-sample-strength-training.kent) |
| <img src="icon-swimming.svg" width="56" alt=""> | Swimming | 26 sessions, one per day through August 2026 (Sundays off), 25&nbsp;m indoor pool, freestyle<br>Aug 1–31, 2026 · indoor pool (no GPS)<br>Avg 20.9 min · 41 lengths/session | [`cordelia-sample-swimming.sqlite`](../example-data/cordelia-sample-swimming.sqlite) | [`.kent`](../example-data/cordelia-sample-swimming.kent) |
| <img src="icon-empty.svg" width="56" alt=""> | Empty | Full schema, no activity data: a blank starting point<br>130 tables, with only Cordelia's seeded lookup tables populated (27,768 rows: 23,778 in `better_labels_lookup`, 3,963 in `better_labels_definitions`, plus the file- and field-type lookups) | [`cordelia-sample-empty.sqlite`](../example-data/cordelia-sample-empty.sqlite) | [`.kent`](../example-data/cordelia-sample-empty.kent) |

Pick the sport closest to your own activity data, or the empty one to explore the schema itself,
then see [Getting started](README.md) for a walkthrough of each.

## Verifying a download

Each database ships with a SHA-256 checksum and a detached GPG signature, signed with the same key
Cordelia's own downloads use. The public key is
[`example-data/cordelia-signing-key.asc`](../example-data/cordelia-signing-key.asc):

```bash
# from inside example-data/
sha256sum -c cordelia-sample-running.sqlite.sha256

gpg --import cordelia-signing-key.asc   # once, to trust the key
gpg --verify cordelia-sample-running.sqlite.asc cordelia-sample-running.sqlite

# the .kent archives are checked and verified the same way
sha256sum -c cordelia-sample-running.kent.sha256
gpg --verify cordelia-sample-running.kent.asc cordelia-sample-running.kent
```

Swap in whichever sport's filename you downloaded.

## Data hygiene

This repo never contains real personal fitness data. The six databases above are entirely
fabricated; none of them is a real person's Cordelia export. Anything else you run a report script
against is a Cordelia database of your own, and it never touches this repo.
