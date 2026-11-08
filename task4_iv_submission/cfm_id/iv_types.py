"""Potential-response-type enumeration for the binary IV model."""
from __future__ import annotations
from itertools import product
from typing import NamedTuple

class IVType(NamedTuple):
    d0: int
    d1: int
    y0: int
    y1: int

def enumerate_types(monotonicity: bool = False) -> list[IVType]:
    """Return all (D(0), D(1), Y(0), Y(1)) types.

    Without monotonicity there are 16 types. With D(1) >= D(0), there are 12.
    """
    out = []
    for d0, d1, y0, y1 in product((0, 1), repeat=4):
        if monotonicity and d1 < d0:
            continue
        out.append(IVType(d0, d1, y0, y1))
    return out
