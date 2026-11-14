"""Exact probability-model checks; no extractor or protocol is implemented."""

from fractions import Fraction as F
from itertools import product
import unittest

from labrador_repair.extraction_bounds import (
    collision_loss_envelope, finite_bad_mass_upper, finite_upper_root_certified,
    finite_witness_lower, gated_bad_mass_upper, gated_upper_root_certified,
    gated_witness_lower, simple_gated_root_upper,
)


def canonical(masses):
    total = sum(masses, F(0))
    return total-max(masses, default=F(0)), total*total-sum((p*p for p in masses), F(0))


def gate_mass_allowed(bad, kappa, eta_0, h):
    difference = bad*bad-kappa*bad-eta_0
    return difference <= 0 or difference*difference <= h*bad


def finite_mass_allowed(bad, delta, eta_0, h):
    difference = delta*bad-eta_0
    return difference <= 0 or difference*difference <= h*bad


class RefinedExtractionBounds(unittest.TestCase):
    def test_weighted_common_anchor_mass_and_selector_factor(self):
        tables = [tuple(F(n, 4) for n in row) for row in product(range(5), repeat=3) if sum(row) <= 4]
        weights = (F(1, 3), F(2, 3))
        for left, right in product(tables, repeat=2):
            pairs = (canonical(left), canonical(right))
            for flags in product((0, 1), repeat=2):
                bad = sum((w*flag for w, flag in zip(weights, flags)), F(0))
                error = sum((w*flag*pair[0] for w, flag, pair in zip(weights, flags, pairs)), F(0))
                eta = sum((w*pair[1] for w, pair in zip(weights, pairs)), F(0))
                self.assertLessEqual(error*error, bad*eta)
        # One selected coordinate out of three: deleting r is invalid even here.
        error, collision = canonical((F(1, 2), F(1, 2)))
        eta_y = collision/3
        self.assertGreater(error*error, eta_y)
        self.assertLessEqual(error*error, 3*eta_y)

    def test_disjoint_branch_and_rational_H_envelope(self):
        grid = (F(0), F(1, 16), F(1, 4), F(1, 2))
        for hroot, yroot, groot in product(grid, repeat=3):
            eta_h, eta_y, eta_g = hroot*hroot, yroot*yroot/3, groot*groot
            h = collision_loss_envelope(3, eta_h, eta_y, eta_g)
            exact_squared = (hroot+yroot)**2+groot*groot
            self.assertEqual(h-exact_squared, (hroot-yroot)**2)
            for nroot, groot_mass in product(grid, repeat=2):
                weighted = nroot*(hroot+yroot)+groot_mass*groot
                mass = nroot*nroot+groot_mass*groot_mass
                self.assertLessEqual(weighted*weighted, mass*exact_squared)
        self.assertEqual(collision_loss_envelope(3, F(1, 64), F(1, 128), F(1, 32)), F(7, 64))
        self.assertEqual(collision_loss_envelope(2, F(1), F(1), F(1)), F(7))

    def test_gate_upper_root_implication_on_independent_mass_grid(self):
        for kappa, a, c in product((F(0), F(1, 16), F(1, 2)),
                                    (F(0), F(1, 16), F(1, 4)),
                                    (F(0), F(1, 16), F(1, 4))):
            eta_0, h = a*a, c**3
            upper = simple_gated_root_upper(kappa, eta_0, h, a, c)
            self.assertEqual(upper, kappa+a+c)
            self.assertTrue(gated_upper_root_certified(kappa, eta_0, h, upper))
            probability_upper = gated_bad_mass_upper(kappa, eta_0, h, upper)
            for numerator in range(65):
                bad = F(numerator, 64)
                if gate_mass_allowed(bad, kappa, eta_0, h):
                    self.assertLessEqual(bad, probability_upper)
        self.assertEqual(gated_bad_mass_upper(F(1, 2), F(0), F(8), F(3)), F(1))

    def test_spurious_zero_and_nonnegative_branch_boundaries(self):
        self.assertTrue(gated_upper_root_certified(F(0), F(0), F(0), F(0)))
        self.assertFalse(gated_upper_root_certified(F(0), F(0), F(1, 8), F(0)))
        self.assertTrue(gated_upper_root_certified(F(0), F(0), F(1, 8), F(1, 2)))
        self.assertFalse(gated_upper_root_certified(F(0), F(0), F(1, 8), F(1, 4)))
        self.assertFalse(gated_upper_root_certified(F(1, 4), F(0), F(0), F(0)))
        self.assertTrue(gated_upper_root_certified(F(1, 4), F(0), F(0), F(1, 4)))
        self.assertFalse(gated_upper_root_certified(F(0), F(1, 4), F(0), F(1, 4)))
        with self.assertRaises(ValueError):
            gated_bad_mass_upper(F(0), F(0), F(1, 8), F(0))
        self.assertTrue(finite_upper_root_certified(F(1, 4), F(0), F(0), F(0)))
        self.assertFalse(finite_upper_root_certified(F(1, 4), F(0), F(1, 16), F(0)))
        self.assertTrue(finite_upper_root_certified(F(1, 4), F(0), F(1, 16), F(1)))

    def test_finite_non_gated_formula_and_the_gate_negative_control(self):
        for delta, eta_0, h in product((F(1, 16), F(1, 4), F(1, 2)),
                                        (F(0), F(1, 256), F(1, 4)),
                                        (F(0), F(1, 256), F(1, 16))):
            simple = 2*eta_0/delta+h/delta**2
            self.assertTrue(finite_upper_root_certified(delta, eta_0, h, simple))
            upper = finite_bad_mass_upper(delta, eta_0, h)
            for numerator in range(65):
                bad = F(numerator, 64)
                if finite_mass_allowed(bad, delta, eta_0, h):
                    self.assertLessEqual(bad, upper)
        # A valid gate root can fail as a finite root, and B=1 is finite-feasible.
        self.assertTrue(gated_upper_root_certified(F(0), F(0), F(1, 16), F(1, 2)))
        self.assertFalse(finite_upper_root_certified(F(1, 4), F(0), F(1, 16), F(1, 2)))
        self.assertTrue(finite_mass_allowed(F(1), F(1, 4), F(0), F(1, 16)))
        self.assertFalse(gate_mass_allowed(F(1), F(0), F(0), F(1, 16)))
        with self.assertRaises(ValueError):
            finite_bad_mass_upper(F(1, 4), F(0), F(1, 16), root_upper=F(1, 2))
        self.assertEqual(finite_bad_mass_upper(F(1, 10), F(1, 100), F(0)), F(1, 5))
        self.assertEqual(finite_bad_mass_upper(F(1, 10), F(1, 100), F(0), root_upper=F(1, 10)), F(1, 10))

    def test_witness_subtractions_and_probability_clipping(self):
        lower = gated_witness_lower(F(1, 2), F(1, 16), 3, 256,
                                    F(0), F(0), F(0), root_upper=F(1, 16))
        self.assertEqual(lower, F(109, 256))  # kappa is inside the root, once.
        self.assertEqual(gated_witness_lower(F(0), F(0), 3, 256,
                                            F(0), F(0), F(0), root_upper=F(0)), F(0))
        self.assertEqual(finite_witness_lower(F(3, 4), F(1, 16), F(1, 8), F(1, 64),
                                             F(0), F(0), F(0)), F(35, 64))
        self.assertEqual(finite_witness_lower(F(0), F(0), F(1, 8), F(1),
                                             F(1), F(1), F(1)), F(0))

    def test_strict_validation_and_invalid_radical_witnesses(self):
        for r in (0, -1, True, 3.0):
            with self.subTest(r=r), self.assertRaises(ValueError):
                collision_loss_envelope(r, F(0), F(0), F(0))
        for probability in (0, 0.5, True, F(-1), F(2)):
            with self.subTest(probability=probability), self.assertRaises(ValueError):
                collision_loss_envelope(3, probability, F(0), F(0))
        for kappa in (F(1), F(-1), 0.0):
            with self.subTest(kappa=kappa), self.assertRaises(ValueError):
                gated_upper_root_certified(kappa, F(0), F(0), F(1))
        for h, upper in ((F(-1), F(1)), (F(0), F(-1)), (0, F(1)), (F(0), 1)):
            with self.subTest(h=h, upper=upper), self.assertRaises(ValueError):
                gated_upper_root_certified(F(0), F(0), h, upper)
        with self.assertRaises(ValueError):
            simple_gated_root_upper(F(0), F(1, 4), F(0), F(1, 4), F(0))
        with self.assertRaises(ValueError):
            simple_gated_root_upper(F(0), F(0), F(1, 8), F(0), F(1, 4))
        for delta in (F(0), F(1), F(-1), 0.5):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                finite_bad_mass_upper(delta, F(0), F(0))
        with self.assertRaises(ValueError):
            finite_witness_lower(F(1), F(1, 2), F(1, 2), F(0), F(0), F(0), F(0))
        for count in (0, 2, True, 256.0):
            with self.subTest(count=count), self.assertRaises(ValueError):
                gated_witness_lower(F(1), F(0), 3, count, F(0), F(0), F(0), root_upper=F(0))


if __name__ == "__main__":
    unittest.main()
