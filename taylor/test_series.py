import math
import unittest
from fractions import Fraction
from itertools import islice

from functions import cos, exp, log1p, sin, taylor
from series import Series


def nth(iterable, n):
    return next(islice(iterable, n, None))


class SeriesTest(unittest.TestCase):
    def test_coefficients_are_computed_once_and_only_on_demand(self):
        calls = []

        def coefficient(n):
            calls.append(n)
            return n

        s = Series(coefficient)
        self.assertEqual(calls, [])
        self.assertEqual(s[3], 3)
        self.assertEqual(s[1], 1)
        self.assertEqual(calls, [0, 1, 2, 3])

    def test_arithmetic(self):
        a = Series.of([1, 2])
        b = Series.of([3, 0, 1])
        self.assertEqual((a + b).take(4), [4, 2, 1, 0])
        self.assertEqual((a - b).take(4), [-2, 2, -1, 0])
        self.assertEqual((a * b).take(5), [3, 6, 1, 2, 0])
        self.assertEqual((2 * a + 1).take(3), [3, 4, 0])

    def test_derivative_undoes_integral(self):
        s = Series(lambda n: n + 1)
        self.assertEqual(s.integral(7).derivative().take(6), s.take(6))


class FunctionsTest(unittest.TestCase):
    def test_distant_coefficients_of_fresh_recursive_series(self):
        self.assertEqual(log1p.integral()[5000], Fraction(1, 5000 * 4999))
        self.assertEqual((sin * cos).derivative()[399], 0)

    def test_exp(self):
        self.assertEqual(exp.take(6), [Fraction(1, math.factorial(n)) for n in range(6)])

    def test_sin_and_cos(self):
        self.assertEqual(sin.take(6), [0, 1, 0, Fraction(-1, 6), 0, Fraction(1, 120)])
        self.assertEqual(cos.take(5), [1, 0, Fraction(-1, 2), 0, Fraction(1, 24)])

    def test_pythagorean_identity(self):
        self.assertEqual((sin * sin + cos * cos).take(12), [1] + [0] * 11)

    def test_exp_turns_sums_into_products(self):
        # e^x * e^x has the series of e^(2x), whose coefficients are 2^n / n!.
        self.assertEqual(
            (exp * exp).take(8),
            [Fraction(2 ** n, math.factorial(n)) for n in range(8)],
        )

    def test_log1p(self):
        self.assertEqual(log1p.take(5), [0, 1, Fraction(-1, 2), Fraction(1, 3), Fraction(-1, 4)])

    def test_taylor_from_derivatives(self):
        # Every derivative of e^x at 0 is 1.
        self.assertEqual(taylor(lambda n: 1).take(8), exp.take(8))

    def test_partial_sums_converge(self):
        self.assertAlmostEqual(float(nth(exp.partial_sums(1), 20)), math.e, places=12)
        self.assertAlmostEqual(float(nth(sin.partial_sums(Fraction(1, 2)), 20)), math.sin(0.5), places=12)
        self.assertAlmostEqual(float(nth(log1p.partial_sums(Fraction(1, 2)), 60)), math.log(1.5), places=12)


if __name__ == "__main__":
    unittest.main()
