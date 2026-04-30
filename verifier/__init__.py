"""Verifier kernel: programmatic + LLM-as-judge."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VerifierResult:
    """Common return type for all verifiers."""

    passed: bool
    score: float
    details: dict[str, Any] = field(default_factory=dict)
