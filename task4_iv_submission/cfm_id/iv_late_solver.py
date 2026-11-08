"""Wald/LATE identification for binary Z, D, Y."""
from __future__ import annotations
from .iv_contract import validate_observed

def _mean_y(observed, z):
    return sum(y * observed[z, d, y] for d in (0, 1) for y in (0, 1))

def _mean_d(observed, z):
    return sum(d * observed[z, d, y] for d in (0, 1) for y in (0, 1))

def identify_late(observed, *, assumptions_accepted: bool, tol: float = 1e-10) -> dict:
    """Compute LATE = ITT_Y / ITT_D after explicit assumption approval.

    This function does not infer or verify substantive independence/exclusion/
    monotonicity from the observed table. Those are scientific assumptions.
    """
    if not assumptions_accepted:
        return {"status": "STOP", "reason": "Required IV assumptions have not been accepted."}
    p = validate_observed(observed)
    itt_y = _mean_y(p, 1) - _mean_y(p, 0)
    first_stage = _mean_d(p, 1) - _mean_d(p, 0)
    if abs(first_stage) <= tol:
        return {"status": "STOP", "reason": "Zero first stage: Wald denominator is zero.",
                "itt_y": itt_y, "first_stage": first_stage}
    if first_stage < 0:
        return {"status": "STOP", "reason": "Negative first stage conflicts with the accepted coding D(1)>=D(0).",
                "itt_y": itt_y, "first_stage": first_stage}
    value = itt_y / first_stage
    if value < -tol or value > 1 + tol:
        return {"status": "CONFLICT", "reason": "Wald ratio lies outside [-1,1] for binary outcomes; inspect assumptions/data.",
                "itt_y": itt_y, "first_stage": first_stage, "late": value}
    return {"status": "POINT", "estimand": "LATE for compliers",
            "late": value, "itt_y": itt_y, "first_stage": first_stage}
