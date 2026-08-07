# antonio

Examples of how to generate reports using Python for a Cordelia database.

`antonio` is the "seed" layer for Cordelia's SQLite output: a handful of basic report scripts,
meant to be read and copied, not a maintained tool, plus the getting-started documentation for
them — see [`docs/namesake.md`](docs/namesake.md) for where the name comes from. For more on
Cordelia itself, see [venholaconsulting.ca/apps/help/](https://venholaconsulting.ca/apps/help/).

**Status:** report/plotting scripts are not written yet. Skeleton getting-started pages exist for
all four sports — see [`docs/getting-started.md`](docs/getting-started.md) — as a target for that
work, not the finished thing.

Four pre-built example databases ship directly in this repo — see [`example-data/`](example-data/)
below — so you don't need any data of your own, or to build anything yourself, just to get
started.

## Example databases

Four pre-built, synthetic Cordelia databases, one per sport — running, cycling, kayaking, strength
training — in [`example-data/`](example-data/):

| File | Sport |
|---|---|
| `cordelia-sample-running.sqlite` | Running (30 daily 5&nbsp;km runs) |
| `cordelia-sample-cycling.sqlite` | Cycling (4 rides, Tour de Victoria route) |
| `cordelia-sample-kayaking.sqlite` | Kayaking (8 paddles) |
| `cordelia-sample-strength-training.sqlite` | Strength training (8 sessions) |

All four are entirely fabricated — no real person, device, or activity is represented.

Each ships with a SHA-256 checksum and a detached GPG signature, signed with the same key used
for Cordelia's own downloads (public key:
[`example-data/cordelia-signing-key.asc`](example-data/cordelia-signing-key.asc)):

```bash
# from inside example-data/
sha256sum -c cordelia-sample-running.sqlite.sha256

gpg --import cordelia-signing-key.asc   # once, to trust the key
gpg --verify cordelia-sample-running.sqlite.asc cordelia-sample-running.sqlite
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` (pandas, matplotlib) is a forward declaration for the report scripts — nothing
in this repo needs it yet.

## Repository layout

| Path | Contents |
|---|---|
| `example-data/` | The four pre-built example databases, their checksums/signatures, and the public signing key — see "Example databases" above. |
| `docs/` | Skeleton getting-started pages (one per sport, plus obtaining data and the namesake story), plus their illustrations — see [`docs/getting-started.md`](docs/getting-started.md). |
| `requirements.txt` | Forward declaration for the report scripts (pandas, matplotlib). |

## Data hygiene

This repo never contains real personal fitness data. The four databases in `example-data/` are
entirely fabricated — nothing in this repo is a real person's real Cordelia export. Whatever you
run a report script against beyond those four is a real Cordelia database of your own, which never
touches this repo.
