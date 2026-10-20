"""Watch Taylor polynomials close in on the functions they expand."""

import math
from fractions import Fraction
from itertools import islice

from functions import cos, exp, log1p, sin

CASES = [
    ("exp", exp, Fraction(1), math.exp),
    ("sin", sin, Fraction(1), math.sin),
    ("cos", cos, Fraction(1), math.cos),
    ("log(1+x)", log1p, Fraction(1, 2), math.log1p),
]

TERMS = 12

for name, series, x, exact in CASES:
    target = exact(x)
    print(f"{name} at x = {x}: first coefficients {[str(c) for c in series.take(6)]}")
    for n, approx in enumerate(islice(series.partial_sums(x), TERMS)):
        print(f"  degree {n:2}  {float(approx):.12f}  error {abs(float(approx) - target):.2e}")
    print()
