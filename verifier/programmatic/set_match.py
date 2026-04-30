"""Set-equality verifier (order-independent, optional case-folding)."""

from __future__ import annotations

import re

from .. import VerifierResult


_SPLIT = re.compile(r"[,\n;]+")


def _to_set(value, *, case_fold: bool) -> set[str]:
    if isinstance(value, (list, tuple, set)):
        items = [str(x).strip() for x in value]
    else:
        items = [s.strip() for s in _SPLIT.split(str(value)) if s.strip()]
    if case_fold:
        items = [x.casefold() for x in items]
    return set(items)


def set_match(agent_output: str, gold: dict) -> VerifierResult:
    case_fold = bool(gold.get("case_insensitive", True))
    expected = _to_set(gold.get("value", []), case_fold=case_fold)
    actual = _to_set(agent_output, case_fold=case_fold)
    passed = expected == actual
    return VerifierResult(
        passed=passed,
        score=1.0 if passed else 0.0,
        details={
            "expected": sorted(expected),
            "actual": sorted(actual),
            "missing_from_actual": sorted(expected - actual),
            "extra_in_actual": sorted(actual - expected),
        },
    )
