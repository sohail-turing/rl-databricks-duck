"""Statistical primitives for verification.

Implements `validator.md` §5: one-sided Fisher's exact + odds ratio with
Haldane-Anscombe 0.5 correction.

Pure Python so it can run anywhere; uses `scipy` if available for the exact test
and falls back to a hand-rolled hypergeometric tail otherwise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

try:
    from scipy.stats import fisher_exact
    _HAVE_SCIPY = True
except ImportError:  # pragma: no cover
    _HAVE_SCIPY = False


Direction = Literal["distractor", "anchor"]


@dataclass
class FisherResult:
    p_value: float
    odds_ratio: float
    direction: Direction
    verified: bool
    k_W: int
    n_W: int
    k_Wp: int
    n_Wp: int

    def as_dict(self) -> dict:
        return {
            "p_value": self.p_value,
            "odds_ratio": self.odds_ratio,
            "direction": self.direction,
            "verified": self.verified,
            "W":  {"passes": self.k_W,  "fails": self.n_W  - self.k_W},
            "Wp": {"passes": self.k_Wp, "fails": self.n_Wp - self.k_Wp},
        }


def _haldane_odds_ratio(k_W: int, n_W: int, k_Wp: int, n_Wp: int) -> float:
    """OR with 0.5 correction so zero cells don't crash the ratio."""
    a = k_W   + 0.5
    b = (n_W  - k_W)  + 0.5
    c = k_Wp  + 0.5
    d = (n_Wp - k_Wp) + 0.5
    return (a * d) / (b * c)


def _fisher_one_sided(k_W: int, n_W: int, k_Wp: int, n_Wp: int, *, direction: Direction) -> float:
    """One-sided p-value.

    direction='distractor' -> H1: success(W') > success(W)  (right tail on Wp)
    direction='anchor'     -> H1: success(W)  > success(W') (right tail on W)
    """
    if _HAVE_SCIPY:
        if direction == "distractor":
            # Tests OR > 1 on table [[k_Wp, n_Wp-k_Wp], [k_W, n_W-k_W]]
            _, p = fisher_exact(
                [[k_Wp, n_Wp - k_Wp], [k_W, n_W - k_W]],
                alternative="greater",
            )
        else:
            _, p = fisher_exact(
                [[k_W, n_W - k_W], [k_Wp, n_Wp - k_Wp]],
                alternative="greater",
            )
        return float(p)

    # Pure-Python fallback: hypergeometric tail.
    if direction == "distractor":
        return _hypergeom_right_tail(k_Wp, n_Wp, k_W, n_W)
    return _hypergeom_right_tail(k_W, n_W, k_Wp, n_Wp)


def _hypergeom_right_tail(k_a: int, n_a: int, k_b: int, n_b: int) -> float:
    """P(K_a >= k_a) given the row totals and column totals are fixed."""
    n = n_a + n_b
    K = k_a + k_b
    p = 0.0
    upper = min(K, n_a)
    lower = max(0, K - n_b)
    for x in range(k_a, upper + 1):
        p += math.comb(n_a, x) * math.comb(n_b, K - x) / math.comb(n, K)
    if x < lower:  # type: ignore[possibly-undefined]
        return 0.0
    return p


def fisher(
    k_W: int, n_W: int, k_Wp: int, n_Wp: int,
    *, direction: Direction, alpha: float = 0.05, min_or: float = 3.0,
) -> FisherResult:
    """Verify a distractor (`direction='distractor'`) or anchor (`direction='anchor'`).

    Returns a FisherResult. `verified=True` iff p < alpha and OR >= min_or in
    the correct direction.
    """
    p = _fisher_one_sided(k_W, n_W, k_Wp, n_Wp, direction=direction)
    or_ = _haldane_odds_ratio(k_W, n_W, k_Wp, n_Wp)

    if direction == "distractor":
        # OR < 1 means W' has fewer passes than W -> wrong direction
        correct_direction = or_ < 1.0
        # We want success(W') > success(W), so we report 1/OR for symmetry
        reported_or = 1.0 / or_ if or_ > 0 else float("inf")
    else:
        correct_direction = or_ > 1.0
        reported_or = or_

    verified = (p < alpha) and correct_direction and (reported_or >= min_or)
    return FisherResult(
        p_value=p,
        odds_ratio=reported_or,
        direction=direction,
        verified=verified,
        k_W=k_W, n_W=n_W,
        k_Wp=k_Wp, n_Wp=n_Wp,
    )
