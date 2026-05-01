"""Query the local milestone SQLite database using canonical table names."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sqlite3
import sys

try:
    from tabulate import tabulate
except ImportError:  # pragma: no cover
    tabulate = None


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "verification" / "runs" / "tier_c_seed.sqlite"


@dataclass(frozen=True)
class TableMapping:
    canonical_name: str
    local_name: str
    sqlite_name: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SQL against the local SQLite artifact while writing queries with canonical table names."
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB_PATH),
        help="Path to the SQLite file. Defaults to the Tier C milestone artifact.",
    )
    parser.add_argument("--sql", help="Inline SQL to execute.")
    parser.add_argument("--file", help="Path to a .sql file to execute.")
    parser.add_argument("--list-mapping", action="store_true", help="Show canonical-to-SQLite table mappings.")
    parser.add_argument("--list-tables", action="store_true", help="List all physical SQLite tables.")
    parser.add_argument("--show-sql", action="store_true", help="Print the rewritten SQL before execution.")
    args = parser.parse_args()

    sql_sources = int(bool(args.sql)) + int(bool(args.file)) + int(not sys.stdin.isatty())
    info_modes = int(args.list_mapping) + int(args.list_tables)

    if args.sql and args.file:
        parser.error("Use only one SQL source: --sql, --file, or stdin.")
    if sql_sources > 1:
        parser.error("Use only one SQL source: --sql, --file, or stdin.")
    if info_modes and sql_sources:
        parser.error("Choose either an info mode (--list-mapping / --list-tables) or a SQL source.")
    if info_modes > 1:
        parser.error("Use only one info mode at a time.")

    return args


def load_sql(args: argparse.Namespace) -> str | None:
    if args.sql:
        return args.sql
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        incoming = sys.stdin.read()
        return incoming if incoming.strip() else None
    return None


def load_mappings(connection: sqlite3.Connection) -> list[TableMapping]:
    rows = connection.execute(
        """
        select canonical_name, local_name, sqlite_name
        from generation_manifest
        order by length(canonical_name) desc, canonical_name asc
        """
    ).fetchall()
    return [TableMapping(*row) for row in rows]


def rewrite_sql(sql: str, mappings: list[TableMapping]) -> tuple[str, list[tuple[str, str]]]:
    rewritten = sql
    replacements: list[tuple[str, str]] = []

    for mapping in mappings:
        for reference in (mapping.canonical_name, mapping.local_name):
            pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(reference)}(?![A-Za-z0-9_])")
            rewritten, count = pattern.subn(mapping.sqlite_name, rewritten)
            if count:
                replacements.append((reference, mapping.sqlite_name))

    return rewritten, replacements


def render_table(headers: list[str], rows: list[tuple[object, ...]]) -> None:
    if tabulate is not None:
        print(tabulate(rows, headers=headers, tablefmt="github"))
    else:  # pragma: no cover
        print("\t".join(headers))
        for row in rows:
            print("\t".join("" if value is None else str(value) for value in row))

    print(f"\n{len(rows)} row(s)")


def execute_query(connection: sqlite3.Connection, sql: str) -> int:
    cursor = connection.execute(sql)
    if cursor.description is None:
        connection.commit()
        print(f"Statement executed successfully. Rows affected: {cursor.rowcount}")
        return 0

    headers = [column[0] for column in cursor.description]
    rows = [tuple(row) for row in cursor.fetchall()]
    render_table(headers, rows)
    return 0


def list_tables(connection: sqlite3.Connection) -> int:
    rows = connection.execute(
        "select name from sqlite_master where type = 'table' order by name"
    ).fetchall()
    render_table(["table_name"], [tuple(row) for row in rows])
    return 0


def list_mapping(connection: sqlite3.Connection) -> int:
    rows = connection.execute(
        """
        select canonical_name, local_name, sqlite_name, row_count
        from generation_manifest
        order by canonical_name
        """
    ).fetchall()
    render_table(
        ["canonical_name", "local_name", "sqlite_name", "row_count"],
        [tuple(row) for row in rows],
    )
    return 0


def main() -> int:
    args = parse_args()
    sql = load_sql(args)
    database_path = Path(args.db).expanduser().resolve()

    if not database_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {database_path}")

    connection = sqlite3.connect(str(database_path))
    try:
        if args.list_tables:
            return list_tables(connection)
        if args.list_mapping:
            return list_mapping(connection)
        if not sql:
            raise ValueError("Provide --sql, --file, stdin, --list-mapping, or --list-tables.")

        mappings = load_mappings(connection)
        rewritten_sql, replacements = rewrite_sql(sql, mappings)
        if args.show_sql:
            print(rewritten_sql.strip())
            if replacements:
                print()
        return execute_query(connection, rewritten_sql)
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())