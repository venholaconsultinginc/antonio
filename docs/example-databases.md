# Example databases at a glance

Six pre-built, fabricated Cordelia databases ship in [`example-data/`](../example-data/): one per
sport, plus a schema-only empty one. Getting started needs no Garmin device, no Cordelia install
and no data of your own.

| | Sport | Contents | File |
|---|---|---|---|
| <img src="icon-running.svg" width="56" alt=""> | Running | 25 daily ~5&nbsp;km runs along a real public route, Sundays rested<br>Aug 1–29, 2026 · Ottawa River Pathway, Ottawa ON<br>Avg 29.2 min · 5.8 min/km pace | [`cordelia-sample-running.sqlite`](../example-data/cordelia-sample-running.sqlite) |
| <img src="icon-cycling.svg" width="56" alt=""> | Cycling | 4 rides along the real Tour de Victoria 80&nbsp;km road-cycling route<br>Sep 5–26, 2026 · Victoria, BC<br>Avg 204.5 min (~3h25m) · 22.6 km/h avg speed | [`cordelia-sample-cycling.sqlite`](../example-data/cordelia-sample-cycling.sqlite) |
| <img src="icon-kayaking.svg" width="56" alt=""> | Kayaking | 8 out-and-back paddles in the Gulf Islands<br>Sep 4–27, 2026 · Mayne Island, BC<br>Avg 91.6 min (~1h32m) · 45.7&nbsp;km total (~5.7&nbsp;km/paddle) | [`cordelia-sample-kayaking.sqlite`](../example-data/cordelia-sample-kayaking.sqlite) |
| <img src="icon-strength-training.svg" width="56" alt=""> | Strength training | 8 sessions of work sets and rest periods; no GPS, so no distance or speed<br>Sep 1–24, 2026 · indoor (no GPS)<br>Avg 51.3 min · 51 work sets + 50 rest periods/session | [`cordelia-sample-strength-training.sqlite`](../example-data/cordelia-sample-strength-training.sqlite) |
| <img src="icon-swimming.svg" width="56" alt=""> | Swimming | 26 sessions, one per day through August 2026 (Sundays off), 25&nbsp;m indoor pool, freestyle<br>Aug 1–31, 2026 · indoor pool (no GPS)<br>Avg 20.9 min · 41 lengths/session | [`cordelia-sample-swimming.sqlite`](../example-data/cordelia-sample-swimming.sqlite) |
| <img src="icon-empty.svg" width="56" alt=""> | Empty | Full schema, no activity data: a blank starting point<br>129 tables, with only Cordelia's seeded lookup tables populated (19,704 rows: 16,866 in `better_labels_lookup`, 2,811 in `better_labels_definitions`, plus the file- and field-type lookups) | [`cordelia-sample-empty.sqlite`](../example-data/cordelia-sample-empty.sqlite) |

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
```

Swap in whichever sport's filename you downloaded.

## Data hygiene

This repo never contains real personal fitness data. The six databases above are entirely
fabricated; none of them is a real person's Cordelia export. Anything else you run a report script
against is a Cordelia database of your own, and it never touches this repo.
