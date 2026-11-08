"""Input validation and observed-data contract for binary IV."""
from __future__ import annotations
from typing import Mapping, Tuple

Cell = Tuple[int, int, int]  # (z, d, y)

def validate_observed(observed: Mapping[Cell, float], tol: float = 1e-8) -> dict[Cell, float]:
    """Validate P(D=d,Y=y | Z=z), with all eight cells explicitly represented.

    Each Z stratum must sum to one. Values must be finite probabilities.
    """
    import math
    expected = {(z, d, y) for z in (0, 1) for d in (0, 1) for y in (0, 1)}
    if set(observed) != expected:
        missing, extra = expected - set(observed), set(observed) - expected
        raise ValueError(f"Expected exactly 8 (z,d,y) cells; missing={missing}, extra={extra}")
    vals = {}
    for key, value in observed.items():
        if not math.isfinite(float(value)) or value < -tol or value > 1 + tol:
            raise ValueError(f"Invalid probability at {key}: {value}")
        vals[key] = max(0.0, min(1.0, float(value)))
    for z in (0, 1):
        total = sum(vals[z, d, y] for d in (0, 1) for y in (0, 1))
        if abs(total - 1.0) > tol:
            raise ValueError(f"Probabilities conditional on Z={z} sum to {total}, not 1")
    return vals
