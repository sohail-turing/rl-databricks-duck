"""CLI entrypoint for milestone synthetic data generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .milestone import (
    build_tier_a,
    default_users_pool_path,
    write_csvs,
    write_json_schemas,
    write_sqlite,
)
from .tier_b import build_tier_b
from .tier_c import build_tier_c


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the synthetic Databricks workspace data")
    parser.add_argument("--target", choices=["sqlite", "databricks"], required=True)
    parser.add_argument("--out", help="Output path for the generated SQLite database")
    parser.add_argument("--catalog", default="main", help="Unity Catalog name for databricks target")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--build", choices=["tier-a", "tier-b", "tier-c"], default="tier-a")
    parser.add_argument("--csv-dir", help="Optional directory where tables will also be exported as CSV files")
    parser.add_argument("--schema-json-dir", help="Optional directory where JSON schema files will be written")
    parser.add_argument(
        "--users-pool",
        default=str(default_users_pool_path()),
        help="Path to the sanitized users_pool.json seed file",
    )
    args = parser.parse_args()

    if args.scale <= 0:
        parser.error("--scale must be greater than zero")

    if args.target == "sqlite" and not any([args.out, args.csv_dir, args.schema_json_dir]):
        parser.error("Provide at least one output option: --out, --csv-dir, or --schema-json-dir")

    if args.target == "databricks":
        raise NotImplementedError(
            "The databricks target is not wired yet. Use --target sqlite for local milestone validation."
        )

    builders = {
        "tier-a": build_tier_a,
        "tier-b": build_tier_b,
        "tier-c": build_tier_c,
    }
    builder = builders[args.build]
    tables = builder(seed=args.seed, scale=args.scale, users_pool_path=args.users_pool)
    output_path = Path(args.out).expanduser().resolve() if args.out else None
    csv_dir = Path(args.csv_dir).expanduser().resolve() if args.csv_dir else None
    schema_json_dir = Path(args.schema_json_dir).expanduser().resolve() if args.schema_json_dir else None

    if output_path:
        write_sqlite(tables, output_path)

    if csv_dir:
        write_csvs(tables, csv_dir)

    if schema_json_dir:
        write_json_schemas(tables, schema_json_dir)

    if output_path:
        print(f"Wrote {args.build} milestone slice to SQLite at {output_path}")
    if csv_dir:
        print(f"Exported {args.build} milestone slice as CSVs to {csv_dir}")
    if schema_json_dir:
        print(f"Exported {args.build} JSON schemas to {schema_json_dir}")
    for table in tables:
        print(f"- {table.canonical_name} -> {table.sqlite_name}: {len(table.dataframe):,} rows")
    print(f"- manifest -> generation_manifest: {len(tables):,} rows")


if __name__ == "__main__":
    main()
