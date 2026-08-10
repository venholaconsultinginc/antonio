# Downloading example databases

Six pre-built, synthetic Cordelia databases ship directly in this repo under
[`example-data/`](../example-data/) — no Garmin device, no Cordelia install, and no data of your
own required just to get started. See [the at-a-glance table with icons](example-databases.md)
for a quick overview of all six.

| | File | Sport |
|---|---|---|
| <img src="icon-running.svg" width="32" alt=""> | [`cordelia-sample-running.sqlite`](../example-data/cordelia-sample-running.sqlite) | Running (30 daily 5&nbsp;km runs) |
| <img src="icon-cycling.svg" width="32" alt=""> | [`cordelia-sample-cycling.sqlite`](../example-data/cordelia-sample-cycling.sqlite) | Cycling (4 rides, Tour de Victoria route) |
| <img src="icon-kayaking.svg" width="32" alt=""> | [`cordelia-sample-kayaking.sqlite`](../example-data/cordelia-sample-kayaking.sqlite) | Kayaking (8 paddles) |
| <img src="icon-strength-training.svg" width="32" alt=""> | [`cordelia-sample-strength-training.sqlite`](../example-data/cordelia-sample-strength-training.sqlite) | Strength training (8 sessions) |
| <img src="icon-swimming.svg" width="32" alt=""> | [`cordelia-sample-swimming.sqlite`](../example-data/cordelia-sample-swimming.sqlite) | Swimming (26 sessions) |
| <img src="icon-empty.svg" width="32" alt=""> | [`cordelia-sample-empty.sqlite`](../example-data/cordelia-sample-empty.sqlite) | Empty (full schema, zero rows — a blank starting point) |

Pick the sport closest to your own activity data, download the matching `.sqlite` file, and
you're working with real Cordelia-schema data in a couple of minutes — see
[Getting started](README.md) for a walkthrough of each one.

## Verifying a download

Each database ships with a SHA-256 checksum and a detached GPG signature, signed with the same
key used for Cordelia's own downloads (public key:
[`example-data/cordelia-signing-key.asc`](../example-data/cordelia-signing-key.asc)):

```bash
# from inside example-data/
sha256sum -c cordelia-sample-running.sqlite.sha256

gpg --import cordelia-signing-key.asc   # once, to trust the key
gpg --verify cordelia-sample-running.sqlite.asc cordelia-sample-running.sqlite
```

Swap in whichever sport's filename you downloaded.

## Data hygiene

This repo never contains real personal fitness data. The six databases above are entirely
fabricated — nothing in this repo is a real person's real Cordelia export. Whatever you run a
report script against beyond those six is a real Cordelia database of your own, which never
touches this repo.
