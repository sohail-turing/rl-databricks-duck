# Verifier

This folder holds the task-scoring layer.

## Current status

| Area | Status | Notes |
| --- | --- | --- |
| `programmatic/` | usable now | `exact_match`, `numeric_match`, and `set_match` are implemented |
| `judge/` | scaffold only | rubric loading and provider execution are not wired yet |

## Current milestone recommendation

For the first 10-task delivery:

1. prefer `exact_match` for strict string outputs
2. prefer `numeric_match` for values such as fees, balances, and counts
3. prefer `set_match` for unordered answer sets
4. only reach for judge rubrics when a task truly cannot be scored programmatically

## Verifier result contract

Both verifier paths are expected to return a `VerifierResult` with:

```python
@dataclass
class VerifierResult:
    passed: bool
    score: float
    details: dict
```

## Current milestone caveat

Manual anchors and distractors are acceptable for this milestone, but they are not yet part of a live statistical verification loop.
