"""Independent spectral and interval checks for the accelerated exact predicate."""

import itertools
import unittest
from fractions import Fraction as F

from labrador_repair.fourier import (
    _build_certified_table,
    _certified_pi_interval,
    _nearest_integer,
    certified_operator_norm_below,
)


class CertifiedFourier(unittest.TestCase):
    def test_small_degrees_against_closed_spectral_formulas(self):
        paths = set()
        for degree, precisions in ((2, (40,)), (4, (1, 4, 40))):
            for bits in precisions:
                for c in itertools.product(range(-2, 3), repeat=degree):
                    energy = sum(x*x for x in c)
                    for threshold in range(1, 2*degree + 2):
                        margin = threshold**2 - energy
                        if degree == 2:
                            expected = margin > 0
                        else:
                            cross = c[0]*c[1] + c[1]*c[2] + c[2]*c[3] - c[0]*c[3]
                            expected = margin > 0 and margin**2 > 2*cross**2
                        actual, path = certified_operator_norm_below(
                            c, threshold, bits=bits, with_path=True)
                        self.assertEqual(actual, expected)
                        paths.add(path)
        self.assertEqual(paths, {'interval_accept', 'interval_reject', 'exact_fallback'})

    def test_signed_monomial_equalities_and_zero(self):
        for degree in (2, 4, 8, 64):
            self.assertEqual(certified_operator_norm_below(
                (0,)*degree, 1, with_path=True), (True, 'interval_accept'))
            for position in (0, degree//2, degree - 1):
                for value in (-2, -1, 1, 2):
                    c = [0]*degree
                    c[position] = value
                    self.assertFalse(certified_operator_norm_below(c, abs(value)))
                    self.assertTrue(certified_operator_norm_below(c, abs(value) + 1))

    def test_interval_enclosure_and_signed_rounding(self):
        for terms in (1, 2, 3, 7, 24):
            for bits in (2, 8, 40, 80):
                lo, hi = _certified_pi_interval(terms, bits)
                finer_lo, finer_hi = _certified_pi_interval(terms + 10, bits + 10)
                self.assertLessEqual(lo, finer_lo)
                self.assertLess(finer_lo, finer_hi)
                self.assertLessEqual(finer_hi, hi)
        for denominator in range(1, 25):
            for numerator in range(-200, 201):
                value = F(numerator, denominator)
                self.assertLessEqual(abs(_nearest_integer(value) - value), F(1, 2))
        table = _build_certified_table(64)
        self.assertLess(table.polynomial_error_upper, F(1, 2*table.scale))
        self.assertLessEqual(table.pi_width, F(1, 2**79))

    def test_uncertified_precision_and_invalid_inputs_reject(self):
        with self.assertRaises(ValueError):
            _build_certified_table(4, taylor_terms=1)
        with self.assertRaises(ValueError):
            certified_operator_norm_below((0, 0), 1, bits=100)
        for c in ((0,), (1, 0, 0), (3, 0), (True, 0), (1.0, 0)):
            with self.subTest(c=c), self.assertRaises(ValueError):
                certified_operator_norm_below(c, 1)
        for threshold in (0, -1, True, 1.0):
            with self.assertRaises(ValueError):
                certified_operator_norm_below((0, 0), threshold)
        for bits in (0, -1, True, 1.0):
            with self.assertRaises(ValueError):
                certified_operator_norm_below((0, 0), 1, bits=bits)


if __name__ == '__main__':
    unittest.main()
