import pytest
from cfm_id.iv_types import enumerate_types
from cfm_id.iv_late_solver import identify_late
from cfm_id.iv_ate_solver import solve_ate_bounds
from cfm_id.iv_ate_verify import verify_ate_result

OBS = {
    (0,0,0): 1.0, (0,0,1): 0.0, (0,1,0): 0.0, (0,1,1): 0.0,
    (1,0,0): 0.5, (1,0,1): 0.0, (1,1,0): 0.0, (1,1,1): 0.5,
}

def test_type_counts():
    assert len(enumerate_types(False)) == 16
    assert len(enumerate_types(True)) == 12

def test_late():
    r = identify_late(OBS, assumptions_accepted=True)
    assert r["status"] == "POINT"
    assert r["late"] == pytest.approx(1.0)

def test_late_stops_without_assumption_approval():
    assert identify_late(OBS, assumptions_accepted=False)["status"] == "STOP"

def test_ate_monotone_bounds_and_replay():
    r = solve_ate_bounds(OBS, monotonicity=True)
    assert r["status"] == "SHARP_BOUNDS"
    assert r["bounds"] == pytest.approx([0.5, 1.0])
    assert r["type_count"] == 12
    assert verify_ate_result(OBS, r, monotonicity=True)["valid"]

def test_unrestricted_ate_bounds_and_dual_certificate():
    r = solve_ate_bounds(OBS, monotonicity=False)
    assert r["status"] == "SHARP_BOUNDS"
    assert r["type_count"] == 16
    assert r["bounds"] == pytest.approx([0.5, 1.0])
    assert verify_ate_result(OBS, r, monotonicity=False)["valid"]


def test_tampered_dual_certificate_is_rejected():
    r = solve_ate_bounds(OBS, monotonicity=True)
    r["upper_dual"][0] += 0.25
    assert not verify_ate_result(OBS, r, monotonicity=True)["valid"]


def test_zero_first_stage_stops():
    no_first_stage = {
        (0,0,0): .5, (0,0,1): 0, (0,1,0): .5, (0,1,1): 0,
        (1,0,0): .5, (1,0,1): 0, (1,1,0): .5, (1,1,1): 0,
    }
    assert identify_late(no_first_stage, assumptions_accepted=True)["status"] == "STOP"

def test_invalid_probability_table_rejected():
    bad = dict(OBS)
    bad[(0,0,0)] = .8
    with pytest.raises(ValueError):
        solve_ate_bounds(bad)
