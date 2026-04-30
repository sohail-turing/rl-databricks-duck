"""Numeric verifier with normalization (currency, %, k/M/B/T suffixes, scientific)."""

from __future__ import annotations

import math
import re

from .. import VerifierResult


_SUFFIX = {"k": 1e3, "m": 1e6, "b": 1e9, "t": 1e12}
_NUMBER = re.compile(
    r"""
    [-+]?
    (?:\d{1,3}(?:[,_]\d{3})+|\d+)        # 1234 or 1,234 or 1_234
    (?:\.\d+)?                           # optional decimal
    (?:[eE][-+]?\d+)?                    # optional exponent
    """,
    re.VERBOSE,
)


def _parse_number(text: str) -> float | None:
    """Parse 1247, 1,247, $1,247.00, 1.247k, 12.5%, 1.2e6, etc."""
    if text is None:
        return None
    s = str(text).strip().lower()
    if not s:
        return None

    is_percent = s.endswith("%")
    if is_percent:
        s = s[:-1].strip()

    suffix_mult = 1.0
    if s and s[-1] in _SUFFIX:
        suffix_mult = _SUFFIX[s[-1]]
        s = s[:-1].strip()

    s = s.replace("$", "").replace("€", "").replace("£", "").replace("¥", "")
    s = s.replace(",", "").replace("_", "").strip()

    m = _NUMBER.search(s)
    if not m:
        return None
    try:
        value = float(m.group(0).replace(",", "").replace("_", ""))
    except ValueError:
        return None

    value *= suffix_mult
    if is_percent:
        value /= 100.0
    return value


def numeric_match(agent_output: str, gold: dict) -> VerifierResult:
    expected = float(gold["value"])
    tolerance = float(gold.get("tolerance", 0))
    actual = _parse_number(agent_output)

    if actual is None:
        return VerifierResult(
            passed=False,
            score=0.0,
            details={"expected": expected, "tolerance": tolerance, "actual_raw": agent_output, "actual_parsed": None},
        )

    diff = abs(actual - expected)
    passed = diff <= tolerance or math.isclose(actual, expected, rel_tol=1e-9, abs_tol=tolerance)
    return VerifierResult(
        passed=passed,
        score=1.0 if passed else 0.0,
        details={
            "expected": expected,
            "tolerance": tolerance,
            "actual_raw": agent_output,
            "actual_parsed": actual,
            "abs_diff": diff,
        },
    )
