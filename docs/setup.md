# Setup

Everything in `antonio` assumes Python 3 and a terminal. If you're already comfortable with virtual
environments and `pip`, this is all you need:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## What `requirements.txt` installs

`requirements.txt` lists, in plain text, the Python packages the report scripts need.
`pip install -r requirements.txt` reads it and installs each one. That's a standard Python
convention, not something antonio invented.

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

It should print a handful of summary metrics and write PNGs to `reports/output/running/` without
errors. Then head back to [Getting started](README.md) and try another sport, or your own data.
