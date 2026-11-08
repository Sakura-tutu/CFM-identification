"""Synthetic binary-IV example. Run: python -m examples.iv_demo"""
from cfm_id import identify_late, solve_ate_bounds, verify_ate_result

# A valid synthetic population:
# 50% compliers (D0=0,D1=1), 50% never-takers (D0=0,D1=0).
# Complier outcome response: Y0=0, Y1=1; never-taker: Y0=0,Y1=0.
# Therefore first stage=.5 and LATE=1. The full-population ATE is not point identified.
observed = {
    (0,0,0): 1.0, (0,0,1): 0.0, (0,1,0): 0.0, (0,1,1): 0.0,
    (1,0,0): 0.5, (1,0,1): 0.0, (1,1,0): 0.0, (1,1,1): 0.5,
}
print("LATE:", identify_late(observed, assumptions_accepted=True))
for monotonicity in (False, True):
    bounds = solve_ate_bounds(observed, monotonicity=monotonicity)
    print("ATE bounds; monotonicity=", monotonicity, ":", bounds["bounds"],
          "types:", bounds["type_count"])
    print("Certificate verification:",
          verify_ate_result(observed, bounds, monotonicity=monotonicity))
