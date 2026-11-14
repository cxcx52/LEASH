"""Independent exact checks for the optional filtered challenge family."""

import itertools
import unittest
from fractions import Fraction as F
from math import factorial

from labrador_repair.bounds import challenge_cube
from labrador_repair.challenges import (
    exact_operator_norm_below,
    filtered_challenge_count_lower,
    filtered_challenge_profile,
    filtered_tail_certified,
)
from labrador_repair.ring import gcd_mod


class CertifiedChallenges(unittest.TestCase):
    def test_rational_mgf_and_angular_constants(self):
        self.assertEqual(sum((F(1, factorial(k)) for k in range(6)), F(0)), F(163, 60))
        self.assertGreater(F(2), F(49, 25))  # sqrt(2)>7/5.
        for k in range(1, 33):
            self.assertLessEqual(F(2 + 2 * 4**k, 5), F(factorial(2*k), factorial(k)))

    def test_integer_tail_and_count_certificates(self):
        self.assertFalse(filtered_tail_certified(64, 30))
        self.assertTrue(filtered_tail_certified(64, 31))
        self.assertTrue(filtered_tail_certified(64, 31, F(7, 16)))
        self.assertEqual(filtered_challenge_count_lower(64, 31), 5**64 // 2 + 1)
        lower = filtered_challenge_count_lower(64, 31, F(7, 16))
        self.assertEqual(lower, 9 * 5**64 // 16 + 1)
        self.assertGreater(lower, F(9, 16) * 5**64)
        self.assertLessEqual(lower - 1, F(9, 16) * 5**64)
        with self.assertRaises(ValueError):
            filtered_challenge_count_lower(64, 30)
        # In this small case the entire cube is independently enumerable.
        observed = sum(exact_operator_norm_below(c, 4)
                       for c in itertools.product(range(-2, 3), repeat=2))
        self.assertEqual(observed, 25)
        self.assertLessEqual(filtered_challenge_count_lower(2, 4), observed)

    def test_challenge_error_terms_are_exact_fractions(self):
        # These terms are statistical only, not a full protocol security budget.
        lower = filtered_challenge_count_lower(64, 31)
        self.assertLessEqual(F(112 + 2, lower), F(1, 2**140))
        counts = (112, 33, 15, 8, 7, 5, 4)
        self.assertLessEqual(sum((F(r + 2, lower) for r in counts), F(0)),
                             F(1, 2**139))

    def test_degree_two_against_closed_spectral_formula(self):
        for c in itertools.product(range(-2, 3), repeat=2):
            for threshold in range(1, 5):
                self.assertEqual(exact_operator_norm_below(c, threshold),
                                 sum(x*x for x in c) < threshold**2)

    def test_degree_four_against_independent_radical_formula(self):
        # ||c||_op^2 = energy + sqrt(2)*abs(cross). Compare by exact squaring.
        count_at_four = 0
        for c in itertools.product(range(-2, 3), repeat=4):
            energy = sum(x*x for x in c)
            cross = c[0]*c[1] + c[1]*c[2] + c[2]*c[3] - c[0]*c[3]
            for threshold in range(1, 7):
                margin = threshold**2 - energy
                expected = margin > 0 and margin**2 > 2*cross**2
                actual = exact_operator_norm_below(c, threshold)
                self.assertEqual(actual, expected)
                if threshold == 4 and actual:
                    count_at_four += 1
        self.assertEqual(count_at_four, 449)

    def test_strict_boundary_and_degree_64_examples(self):
        constant_two = (2,) + (0,) * 63
        self.assertFalse(exact_operator_norm_below(constant_two, 2))
        self.assertTrue(exact_operator_norm_below(constant_two, 31))
        self.assertTrue(exact_operator_norm_below((0,) * 64, 31))
        self.assertFalse(exact_operator_norm_below((2,) * 64, 31))

    def test_profile_uses_existing_unit_condition_and_leaves_cube_unchanged(self):
        before = challenge_cube(64)
        profile = filtered_challenge_profile(4294967197)
        self.assertEqual(profile["operator_norm_strictly_below"], 31)
        self.assertEqual(profile["cardinality_lower_bound_inclusive"], 9 * 5**64 // 16 + 1)
        self.assertEqual(profile["acceptance_probability_strictly_greater_than"], F(9, 16))
        self.assertEqual(profile["expected_candidate_draws_strictly_less_than"], F(16, 9))
        self.assertTrue(profile["zero_is_included"])
        self.assertEqual(profile["l2_norm_squared_upper_bound"], 256)
        self.assertEqual(challenge_cube(64), before)
        self.assertEqual(before["operator_norm_bound"], 128)
        with self.assertRaises(ValueError):
            filtered_challenge_profile(13, degree=2, threshold=4, rejection_upper=F(1, 2))
        self.assertNotEqual(gcd_mod((2, 3), (1, 0, 1), 13), (1,))
        # The existing repairs suite already enumerates every d4 cube difference.

    def test_invalid_inputs_do_not_turn_into_certificates(self):
        for degree in (0, 1, 3, True, 64.0):
            with self.subTest(degree=degree), self.assertRaises(ValueError):
                filtered_tail_certified(degree, 31)
        for threshold in (0, -1, True, 31.0):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                filtered_tail_certified(64, threshold)
        for rejection in (F(0), F(1), F(-1, 2), 0.5):
            with self.subTest(rejection=rejection), self.assertRaises(ValueError):
                filtered_tail_certified(64, 31, rejection)
        for coefficients in ((3, 0), (True, 0), (1.0, 0), (1, 2, 1)):
            with self.subTest(coefficients=coefficients), self.assertRaises(ValueError):
                exact_operator_norm_below(coefficients, 31)


if __name__ == "__main__":
    unittest.main()
