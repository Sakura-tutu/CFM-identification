"""Sharp ATE bounds via a finite latent response-type linear program."""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from .iv_contract import validate_observed
from .iv_types import enumerate_types


def build_lp(observed, *, monotonicity: bool = False):
    """Build A_eq p=b_eq for P(D=d,Y=y | Z=z).

    A latent type is t=(D(0),D(1),Y(0),Y(1)); under consistency and exclusion,
    D=D(Z) and Y=Y(D). Each column of A corresponds to one admissible type.
    """
    p = validate_observed(observed)
    types = enumerate_types(monotonicity)
    rows, rhs = [], []
    for z in (0, 1):
        for d in (0, 1):
            for y in (0, 1):
                rows.append([
                    1.0 if ((t.d0 if z == 0 else t.d1) == d
                            and (t.y0 if d == 0 else t.y1) == y) else 0.0
                    for t in types
                ])
                rhs.append(p[z, d, y])
    # The eight observed-cell equations imply sum(p)=1 (one equation is redundant).
    c = np.asarray([t.y1 - t.y0 for t in types], dtype=float)
    return types, np.asarray(rows), np.asarray(rhs), c


def solve_ate_bounds(observed, *, monotonicity: bool = False):
    """Return sharp model bounds, primal endpoint witnesses, and dual certificates."""
    types, A, b, c = build_lp(observed, monotonicity=monotonicity)
    lo = linprog(c, A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    hi = linprog(-c, A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    if not lo.success or not hi.success:
        return {
            "status": "INFEASIBLE",
            "lower_solver_message": lo.message,
            "upper_solver_message": hi.message,
            "type_count": len(types),
        }

    # Equality duals from HiGHS. For min(c'x), A'lambda <= c.
    # For max(c'x), sign-flip the dual of min(-c'x): A'mu >= c.
    lower_dual = np.asarray(lo.eqlin.marginals, dtype=float)
    upper_dual = -np.asarray(hi.eqlin.marginals, dtype=float)
    return {
        "status": "SHARP_BOUNDS",
        "estimand": "ATE = E[Y(1)-Y(0)]",
        "bounds": [float(lo.fun), float(-hi.fun)],
        "monotonicity": monotonicity,
        "type_count": len(types),
        "types": [tuple(t) for t in types],
        "lower_witness": lo.x.tolist(),
        "upper_witness": hi.x.tolist(),
        "lower_dual": lower_dual.tolist(),
        "upper_dual": upper_dual.tolist(),
        "lower_objective": float(np.dot(c, lo.x)),
        "upper_objective": float(np.dot(c, hi.x)),
        "solver": "scipy.optimize.linprog(method='highs')",
    }
