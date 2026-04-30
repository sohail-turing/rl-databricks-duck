"""Exact-string match verifier."""

from __future__ import annotations

from .. import VerifierResult


def exact_match(agent_output: str, gold: dict) -> VerifierResult:
    expected = str(gold.get("value", "")).strip()
    accepted = {str(x).strip() for x in gold.get("accepted_formats", [])}
    accepted.add(expected)

    actual = (agent_output or "").strip()
    passed = actual in accepted
    return VerifierResult(
        passed=passed,
        score=1.0 if passed else 0.0,
        details={"expected": expected, "accepted_formats": sorted(accepted), "actual": actual},
    )
