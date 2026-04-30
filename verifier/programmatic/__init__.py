"""Programmatic verifiers.

A registry maps `spec` strings (used in task YAMLs) to verifier callables.
Each verifier takes (agent_output, gold_spec) and returns a VerifierResult.
"""

from __future__ import annotations

from typing import Callable

from .. import VerifierResult
from .exact_match import exact_match
from .set_match import set_match
from .numeric_match import numeric_match

VerifierFn = Callable[[str, dict], VerifierResult]

REGISTRY: dict[str, VerifierFn] = {
    "exact_match": exact_match,
    "set_match": set_match,
    "numeric_match": numeric_match,
    # frame_match: TODO in WS-8
}


def get(spec: str) -> VerifierFn:
    if spec not in REGISTRY:
        raise KeyError(f"Unknown programmatic verifier spec: {spec!r}. Known: {list(REGISTRY)}")
    return REGISTRY[spec]
