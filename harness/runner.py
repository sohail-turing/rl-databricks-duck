"""Harness CLI.

Stub. Implemented in WS-8.

Examples:
    python -m harness.runner --task T-001 --run-id local-001
    python -m harness.runner --suite tasks/ --concurrency 4
    python -m harness.runner --task T-042 --claim D-3 --ablation on --runs 30
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Run tasks and verification ablations")
    parser.add_argument("--task", help="Single task id (e.g. T-001)")
    parser.add_argument("--suite", help="Directory of task YAMLs to run as a suite")
    parser.add_argument("--run-id", help="Run identifier (defaults to a timestamp)")
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--claim", help="Verification claim id (e.g. D-3 or A-1)")
    parser.add_argument("--ablation", choices=["off", "on"], default="off",
                        help="When 'on', apply the claim's ablation before running")
    parser.add_argument("--runs", type=int, default=1,
                        help="Number of runs (use 30 for verification per validator.md \u00a75.3)")
    args = parser.parse_args()

    raise NotImplementedError(
        f"WS-8 stub: task={args.task} suite={args.suite} ablation={args.ablation} runs={args.runs}"
    )


if __name__ == "__main__":
    main()
