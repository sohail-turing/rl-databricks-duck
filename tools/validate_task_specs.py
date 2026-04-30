"""Validate every task YAML against the schema in validator.md \u00a77.

Run as a pre-commit hook; fails with a non-zero exit code on the first
invalid file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REQUIRED_TOP_LEVEL = {
    "id", "domain", "difficulty", "query", "expected_assets",
    "gold_sql", "gold_answer", "verifier", "distractors", "anchors", "output_location",
}
ALLOWED_DOMAINS = {"sales", "marketing", "finance", "engineering"}
ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_VERIFIER_KINDS = {"programmatic", "judge"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        spec = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        return [f"{path}: invalid YAML — {exc}"]

    if not isinstance(spec, dict):
        return [f"{path}: top-level must be a mapping"]

    missing = REQUIRED_TOP_LEVEL - spec.keys()
    if missing:
        errors.append(f"{path}: missing required keys: {sorted(missing)}")

    if spec.get("domain") not in ALLOWED_DOMAINS:
        errors.append(f"{path}: domain must be one of {sorted(ALLOWED_DOMAINS)}, got {spec.get('domain')!r}")

    if spec.get("difficulty") not in ALLOWED_DIFFICULTIES:
        errors.append(f"{path}: difficulty must be one of {sorted(ALLOWED_DIFFICULTIES)}, got {spec.get('difficulty')!r}")

    verifier = spec.get("verifier") or {}
    if verifier.get("kind") not in ALLOWED_VERIFIER_KINDS:
        errors.append(f"{path}: verifier.kind must be one of {sorted(ALLOWED_VERIFIER_KINDS)}")

    for collection in ("distractors", "anchors"):
        for i, claim in enumerate(spec.get(collection) or []):
            if "claim_id" not in claim or "taxonomy_id" not in claim or "asset_ref" not in claim:
                errors.append(f"{path}: {collection}[{i}] missing one of {{claim_id, taxonomy_id, asset_ref}}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-dir", default="tasks")
    args = parser.parse_args()

    all_errors: list[str] = []
    for path in sorted(Path(args.tasks_dir).glob("T-*.yaml")):
        all_errors.extend(validate(path))

    if all_errors:
        for line in all_errors:
            print(line, file=sys.stderr)
        return 1
    print("All task specs are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
