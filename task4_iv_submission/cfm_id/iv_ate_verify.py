"""Independent replay checks for ATE primal witnesses and LP dual certificates."""
from __future__ import annotations

import numpy as np

from .iv_ate_solver import build_lp


def verify_ate_result(observed, result, *, monotonicity: bool = False, tol: float = 1e-7) -> dict:
    """Verify endpoint feasibility and matching dual bounds.

    Lower: primal min c'x, dual max b'lambda s.t. A'lambda <= c.
    Upper: primal max c'x, dual min b'mu s.t. A'mu >= c.
    Matching feasible primal/dual objectives certify optimality by weak duality.
    """
    if result.get("status") != "SHARP_BOUNDS":
        return {"valid": False, "reason": "No successful bounds result to verify."}
    try:
        types, A, b, c = build_lp(observed, monotonicity=monotonicity)
        if result.get("type_count") != len(types) or result.get("monotonicity") != monotonicity:
            return {"valid": False, "reason": "Response-type model does not match verifier settings."}
        bounds = np.asarray(result["bounds"], dtype=float)
        if bounds.shape != (2,) or not np.all(np.isfinite(bounds)) or bounds[0] > bounds[1] + tol:
            return {"valid": False, "reason": "Malformed or reversed bounds."}
    except (KeyError, TypeError, ValueError) as exc:
        return {"valid": False, "reason": f"Invalid result or observed table: {exc}"}

    checks = {}
    for label, primal_key, dual_key, endpoint, sense in (
        ("lower", "lower_witness", "lower_dual", bounds[0], "min"),
        ("upper", "upper_witness", "upper_dual", bounds[1], "max"),
    ):
        try:
            x = np.asarray(result[primal_key], dtype=float)
            lam = np.asarray(result[dual_key], dtype=float)
        except (KeyError, TypeError, ValueError):
            return {"valid": False, "reason": f"Missing or malformed {label} certificate."}
        if x.shape != (len(types),) or lam.shape != (A.shape[0],):
            return {"valid": False, "reason": f"{label} certificate has wrong dimension."}
        if not np.all(np.isfinite(x)) or not np.all(np.isfinite(lam)):
            return {"valid": False, "reason": f"{label} certificate contains non-finite values."}
        checks[f"{label}_primal_nonnegative"] = bool(np.min(x) >= -tol)
        checks[f"{label}_primal_observed_constraints"] = bool(np.max(np.abs(A @ x - b)) <= tol)
        checks[f"{label}_primal_normalization"] = bool(abs(float(x.sum()) - 1.0) <= tol)
        primal_obj = float(c @ x)
        checks[f"{label}_primal_objective"] = bool(abs(primal_obj - endpoint) <= tol)
        dual_lhs = A.T @ lam
        if sense == "min":
            checks[f"{label}_dual_feasible"] = bool(np.max(dual_lhs - c) <= tol)
            dual_obj = float(b @ lam)
            checks[f"{label}_duality_gap"] = bool(abs(primal_obj - dual_obj) <= tol)
        else:
            checks[f"{label}_dual_feasible"] = bool(np.min(dual_lhs - c) >= -tol)
            dual_obj = float(b @ lam)
            checks[f"{label}_duality_gap"] = bool(abs(primal_obj - dual_obj) <= tol)

    return {
        "valid": all(checks.values()),
        "checks": checks,
        "note": "Primal feasibility plus dual feasibility and matching objectives certify both LP endpoints within tolerance.",
    }
