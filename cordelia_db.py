"""Shared helpers for Cordelia's SQLite schema: unit conversions and column lookups.

Schema snapshot: cordelia source, captured 2026-08-06 (post cordelia ticket #72's fix, fossil
commit b2a77bad4b) -- see docs/plan.md for the full encoding writeup and
docs/objectives-and-requirements.md for why this module exists. Before trusting this against a
real cordelia checkout, diff sql/create_tables.sql against the current CREATE TABLE statements
in ../cordelia/src/records/*.cpp.
"""

import re
from datetime import datetime
from pathlib import Path

SQL_DIR = Path(__file__).parent / "sql"
CREATE_TABLES_SQL = SQL_DIR / "create_tables.sql"


def degrees_to_semicircles(degrees: float) -> int:
    """Cordelia/FIT store lat/long as int32 semicircles, not plain degrees."""
    return round(degrees * (2**31) / 180)


def semicircles_to_degrees(semicircles: int) -> float:
    return semicircles * 180 / (2**31)


def to_iso8601(dt: datetime) -> str:
    """Cordelia's fixed 19-char TEXT timestamp format: YYYY-MM-DDTHH:MM:SS, UTC, no offset.

    Validated on read by ISO8601DateTime::try_from_string in cordelia, which rejects anything
    of a different length or with separators in different positions -- see
    cordelia/src/core/iso8601_datetime.cpp:40-54.

    Every timestamp-semantic column this repo writes uses this same encoding, including
    Session.start_time and Lap.start_time -- both were historically inconsistent (see cordelia
    ticket #72, closed/fixed 2026-08-06) but are now uniformly ISO8601DateTime/TEXT, same as
    every other timestamp column. There is no more Garmin-epoch-integer encoding anywhere in
    the tables this repo touches.

    `dt` is treated as naive wall-clock UTC -- it is formatted as-is, with no timezone
    conversion.
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def table_columns(table_name: str) -> list[str]:
    """Column names, in declared order, for one table in sql/create_tables.sql.

    Every table here declares its autoincrement primary key first (file_number for FileID,
    RecordNumber for the other six) -- callers building INSERT statements should skip
    columns[0] and let SQLite assign it.
    """
    sql = CREATE_TABLES_SQL.read_text()
    match = re.search(rf"CREATE TABLE IF NOT EXISTS {table_name} \((.*?)\n\);", sql, re.DOTALL)
    if not match:
        raise ValueError(f"table {table_name!r} not found in {CREATE_TABLES_SQL}")
    columns = []
    for line in match.group(1).splitlines():
        line = line.strip().rstrip(",")
        if not line or line.upper().startswith("UNIQUE("):
            continue
        columns.append(line.split()[0])
    return columns


def _check_columns(table: str, columns) -> None:
    unknown = set(columns) - set(table_columns(table))
    if unknown:
        raise ValueError(f"{table}: not real column(s): {sorted(unknown)}")


def insert_statement(table: str, values: dict) -> str:
    """Build one INSERT statement using only the given columns; every column not present in
    `values` (including the autoincrement primary key, ordinarily) is left for SQLite to default
    to NULL/assign, rather than being spelled out -- with ~85-160 columns on some of these
    tables, writing every column on every row would bloat generated output enormously for no
    benefit. `values` keys are checked against sql/create_tables.sql to catch typos early.
    """
    _check_columns(table, values)
    columns = list(values.keys())
    rendered = ", ".join(sql_literal(values[c]) for c in columns)
    col_list = ", ".join(columns)
    return f"INSERT INTO {table} ({col_list}) VALUES ({rendered});"


def insert_many_statement(table: str, columns: list[str], rows: list[dict]) -> str:
    """Build one multi-row INSERT covering `columns` for every dict in `rows`. The column list
    is written once rather than once per row -- for a table with many rows per generated
    activity (Record), that matters far more than the per-row NULL-column savings above.
    """
    _check_columns(table, columns)
    col_list = ", ".join(columns)
    value_tuples = (
        "(" + ", ".join(sql_literal(row[c]) for c in columns) + ")" for row in rows
    )
    values_sql = ",\n".join(value_tuples)
    return f"INSERT INTO {table} ({col_list}) VALUES\n{values_sql};"


def sql_literal(value) -> str:
    """Render a Python value as a SQL literal for a hand-written INSERT statement.

    Floats are rounded to 3 decimal places: plenty for meters/(m/s)/degrees-C, and Python's
    full 17-significant-digit float repr() would otherwise bloat a file with tens of thousands
    of generated rows for no real precision gain.
    """
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return repr(value)
    if isinstance(value, float):
        return f"{value:.3f}"
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def _self_check():
    for deg in (45.4215, -75.6972, 0.0, -89.9999):
        semis = degrees_to_semicircles(deg)
        back = semicircles_to_degrees(semis)
        assert abs(back - deg) < 1e-4, f"GPS round-trip failed for {deg}: got {back}"

    sample_dt = datetime(2026, 8, 5, 9, 0, 0)
    ts = to_iso8601(sample_dt)
    assert len(ts) == 19 and ts[10] == "T", f"unexpected timestamp format: {ts}"

    assert table_columns("FileID")[0] == "file_number"
    assert table_columns("Record")[0] == "RecordNumber"
    assert "position_lat" in table_columns("Record")
    assert "TEXT" in _column_type("Session", "start_time"), "Session.start_time should be TEXT"
    assert "TEXT" in _column_type("Lap", "start_time"), "Lap.start_time should be TEXT"


def _column_type(table: str, column: str) -> str:
    """Declared type for one column -- used only by the self-check above, to catch a schema
    regression on either of the two columns cordelia ticket #72 fixed."""
    sql = CREATE_TABLES_SQL.read_text()
    match = re.search(rf"CREATE TABLE IF NOT EXISTS {table} \((.*?)\n\);", sql, re.DOTALL)
    for line in match.group(1).splitlines():
        line = line.strip().rstrip(",")
        parts = line.split()
        if parts and parts[0] == column:
            return parts[1]
    raise ValueError(f"{table}.{column} not found")


_self_check()
