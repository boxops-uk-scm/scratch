"""Maclaurin series of familiar functions, defined by the equations they satisfy.

None of these spell out a formula for the n-th coefficient. Each says what the
function's derivative is and what it is worth at 0, and the coefficients fall
out of integrating lazily.
"""

from fractions import Fraction
from math import factorial

from series import Series

# exp' = exp, exp(0) = 1
exp = Series.fix(lambda e: e.integral(1))


def _sin_cos():
    # sin' = cos, cos' = -sin, sin(0) = 0, cos(0) = 1
    sin = Series(lambda n: sin_def[n])
    cos = Series(lambda n: cos_def[n])
    sin_def = cos.integral(0)
    cos_def = (-sin).integral(1)
    return sin, cos


sin, cos = _sin_cos()

# d/dx log(1 + x) = 1 / (1 + x) = 1 - x + x^2 - ...
log1p = Series(lambda n: (-1) ** n).integral(0)


def taylor(derivative):
    """The Taylor series about a point a, where derivative(n) is the n-th
    derivative of the function at a."""
    return Series(lambda n: Fraction(derivative(n)) / factorial(n))
