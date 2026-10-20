"""Power series as lazy, infinite, memoised sequences of coefficients.

A Series stands for a0 + a1*x + a2*x^2 + ... . It is given as a function from n
to a_n, held in a Chimera, so each coefficient is computed at most once and is
found in O(1) once computed. A series may be defined in terms of itself
(exp = 1 + integral of exp) as long as no coefficient depends on itself.

Coefficients are filled in index order up to the one asked for. Every operation
here builds a coefficient from earlier ones, and filling in order keeps that
from becoming one Python call per uncomputed coefficient below it.
"""

from fractions import Fraction
from itertools import count, islice

from chimera import Chimera


class Series:
    def __init__(self, coefficient):
        self._table = Chimera(coefficient)
        self._filled = 0

    @classmethod
    def fix(cls, define):
        """The series s satisfying s = define(s)."""
        s = cls(lambda n: defined[n])
        defined = define(s)
        return s

    @classmethod
    def of(cls, coeffs):
        """A finite list of coefficients, padded with zeros."""
        coeffs = list(coeffs)
        return cls(lambda n: coeffs[n] if n < len(coeffs) else 0)

    def __getitem__(self, n):
        while self._filled < n:
            m = self._filled
            self._filled += 1
            self._table[m]
        return self._table[n]

    def __iter__(self):
        return map(self.__getitem__, count())

    def take(self, n):
        return list(islice(self, n))

    def __add__(self, other):
        other = _lift(other)
        return Series(lambda n: self[n] + other[n])

    __radd__ = __add__

    def __neg__(self):
        return Series(lambda n: -self[n])

    def __sub__(self, other):
        return self + -_lift(other)

    def __rsub__(self, other):
        return _lift(other) - self

    def __mul__(self, other):
        if not isinstance(other, Series):
            return Series(lambda n: other * self[n])
        # Cauchy product: c_n = sum of a_k * b_(n-k).
        return Series(lambda n: sum(self[k] * other[n - k] for k in range(n + 1)))

    __rmul__ = __mul__

    def derivative(self):
        return Series(lambda n: (n + 1) * self[n + 1])

    def integral(self, constant=0):
        return Series(lambda n: constant if n == 0 else self[n - 1] * Fraction(1, n))

    def partial_sums(self, x):
        """The lazy sequence of Taylor polynomials evaluated at x."""
        total, power = 0, 1
        for a in self:
            total += a * power
            power *= x
            yield total


def _lift(value):
    return value if isinstance(value, Series) else Series.of([value])
