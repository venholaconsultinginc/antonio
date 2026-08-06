"""Shared helpers for Cordelia's SQLite schema: unit conversions, column lookups, and direct
SQLite write helpers (schema creation, single/many-row insert with real primary-key readback).

Schema snapshot: cordelia source, captured 2026-08-06 (post cordelia ticket #72's fix, fossil
commit b2a77bad4b) -- see docs/plan.md for the full encoding writeup and
docs/objectives-and-requirements.md for why this module exists. Before trusting this against a
real cordelia checkout, diff sql/create_tables.sql against the current CREATE TABLE statements
in ../cordelia/src/records/*.cpp.
"""

import re
import sqlite3
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


def create_schema(conn: sqlite3.Connection) -> None:
    """Apply sql/create_tables.sql's CREATE TABLE statements to `conn`. Idempotent (every
    statement is CREATE TABLE IF NOT EXISTS), so safe to call against a database that already
    has some or all of these tables.
    """
    conn.executescript(CREATE_TABLES_SQL.read_text())


def insert_row(conn: sqlite3.Connection, table: str, values: dict) -> int:
    """Insert one row into `table` and return its real assigned primary key.

    `values` must not include the table's own autoincrement primary key (column[0] in
    sql/create_tables.sql -- file_number for FileID, RecordNumber for the other six tables):
    the whole point of this helper is that SQLite assigns it, and the caller reads the real
    value back from here, rather than the caller predicting it and hoping the prediction still
    matches whatever SQLite actually assigned. Every other column not present in `values` is
    left for SQLite to default to NULL -- with ~85-160 columns on some of these tables, writing
    every column on every row would be enormous for no benefit. `values` keys are checked
    against sql/create_tables.sql to catch typos early.
    """
    pk_column = table_columns(table)[0]
    if pk_column in values:
        raise ValueError(
            f"{table}.{pk_column} is an autoincrement primary key; do not set it -- "
            f"read the real value back from this function's return value instead"
        )
    _check_columns(table, values)
    columns = list(values.keys())
    placeholders = ", ".join("?" for _ in columns)
    col_list = ", ".join(columns)
    cur = conn.execute(
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders});",
        [values[c] for c in columns],
    )
    return cur.lastrowid


def insert_many(conn: sqlite3.Connection, table: str, columns: list[str], rows: list[dict]) -> None:
    """Insert many rows into `table`, covering `columns` for every dict in `rows`. The column
    list is written once rather than once per row -- for a table with many rows per generated
    activity (Record), that matters far more than the per-row NULL-column savings `insert_row`
    gets from omitting unset columns entirely.
    """
    _check_columns(table, columns)
    col_list = ", ".join(columns)
    placeholders = ", ".join("?" for _ in columns)
    conn.executemany(
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders});",
        [[row[c] for c in columns] for row in rows],
    )


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

    with sqlite3.connect(":memory:") as conn:
        create_schema(conn)
        file_number = insert_row(
            conn, "FileID", {"path": "self-check.fit", "imported_at": ts, "time_created": ts}
        )
        assert file_number == 1, f"expected the first FileID row to get file_number 1, got {file_number}"
        try:
            insert_row(conn, "FileID", {"file_number": 99, "path": "x", "imported_at": ts})
            raise AssertionError("insert_row should reject an explicit primary-key value")
        except ValueError:
            pass
        insert_many(
            conn, "Record", ["file_number", "Distance"], [{"file_number": file_number, "Distance": 1.0}]
        )
        (row_count,) = conn.execute("SELECT COUNT(*) FROM Record").fetchone()
        assert row_count == 1, f"expected 1 Record row, got {row_count}"


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
