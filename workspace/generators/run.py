"""CLI entrypoint for synthetic data generation.

Stub. Implemented in WS-2.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the synthetic Databricks workspace data")
    parser.add_argument("--target", choices=["duckdb", "databricks"], required=True)
    parser.add_argument("--out", help="Output path for duckdb target")
    parser.add_argument("--catalog", default="main", help="Unity Catalog name for databricks target")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--scale", type=float, default=1.0)
    args = parser.parse_args()

    raise NotImplementedError(
        f"WS-2 stub: target={args.target}, seed={args.seed}, scale={args.scale}"
    )


if __name__ == "__main__":
    main()
