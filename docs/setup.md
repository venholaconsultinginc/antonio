# Setup

Everything in `antonio` assumes Python 3 and a terminal. If you're already comfortable with
virtual environments and `pip`, this is all you need:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## What `requirements.txt` installs

`requirements.txt` is a plain-text list of the Python packages the report scripts depend on —
`pip install -r requirements.txt` reads it and installs each one. It's a standard convention
across Python projects, not something specific to antonio.

Currently:

| Package | Used for |
|---|---|
| `pandas` | Loading query results from a Cordelia SQLite database into DataFrames |
| `matplotlib` | The plots each report script produces |

## Checking it worked

Run the finished example script against the bundled running database:

```bash
python3 reports/running_report.py
```

If that prints a handful of summary metrics and writes PNGs to `reports/output/running/` without
errors, your setup is good — head back to [Getting started](README.md) to try it against other
sports or your own data.
