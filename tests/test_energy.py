"""Independent enumeration and rational checks for bounded-energy certificates."""

from fractions import Fraction as F
from itertools import product
from math import factorial
import unittest

from labrador_repair.energy import (
    SymmetricRawMoments, bounded_energy_count_lower, bounded_energy_member,
    bounded_energy_profile, energy_ball_count, energy_ball_rank,
    energy_ball_rejection_upper, energy_ball_unrank, energy_counts,
    energy_shell_count, positive_exponential_lower, raw_energy_ball_moments,
    symmetric_fold_cap_certified, tilted_mgf_certified, tilted_operator_tail_upper,
)
from labrador_repair.ring import negacyclic_multiply


def norm_squared(vector):
    return sum(x*x for x in vector)


def small_spectral_below(c, threshold):
    if len(c) == 2:
        return norm_squared(c) < threshold*threshold
    cross = c[0]*c[1]+c[1]*c[2]+c[2]*c[3]-c[0]*c[3]
    margin = threshold*threshold-norm_squared(c)
    return margin > 0 and margin*margin > 2*cross*cross


def stacked_image(blocks, challenge):
    return tuple(x for block in blocks for x in negacyclic_multiply(block, challenge))


class BoundedEnergyCertificates(unittest.TestCase):
    def test_counts_and_decoder_against_complete_small_spaces(self):
        self.assertEqual(energy_counts(0), (1,))
        self.assertEqual(energy_ball_unrank(0, 0, 0), ())
        self.assertEqual(energy_ball_rank((), 0), 0)
        for d in (1, 2, 3, 4):
            cube = tuple(product(range(-2, 3), repeat=d))
            observed = tuple(sum(norm_squared(c) == e for c in cube) for e in range(4*d+1))
            self.assertEqual(energy_counts(d), observed)
            for cap in (0, min(5, 4*d), 4*d):
                ball = tuple(c for c in cube if norm_squared(c) <= cap)
                self.assertEqual(energy_ball_count(d, cap), len(ball))
                self.assertEqual(energy_shell_count(d, cap), observed[cap])
                for rank, c in enumerate(ball):
                    self.assertEqual(energy_ball_unrank(d, cap, rank), c)
                    self.assertEqual(energy_ball_rank(c, cap), rank)

    def test_shell_71_independent_multinomial_count(self):
        direct = sum(factorial(64)//(factorial(j)*factorial(71-4*j)*factorial(3*j-7))
                     *2**(71-3*j) for j in range(3, 18))
        self.assertEqual(energy_shell_count(64, 71), direct)
        self.assertEqual(direct, 914575309776010636758020194460195880960)
        self.assertLess(direct, 3*2**128)
        self.assertGreater(F(3, direct), F(1, 2**128))

    def test_membership_against_independent_small_spectral_formula(self):
        for d in (2, 4):
            for c in product(range(-2, 3), repeat=d):
                for cap in (0, 5, 4*d):
                    for threshold in (2, 3, 4):
                        expected = norm_squared(c) <= cap and small_spectral_below(c, threshold)
                        self.assertEqual(bounded_energy_member(c, cap, threshold), expected)
        self.assertFalse(bounded_energy_member((2, 0), 4, 2))  # exact equality
        self.assertTrue(bounded_energy_member((0,)*64, 104, 30))
        self.assertFalse(bounded_energy_member((2,)*64, 104, 30))

    def test_raw_non_iid_ball_moments_and_general_variance_formula(self):
        for d, cap in ((2, 3), (4, 5)):
            raw = tuple(c for c in product(range(-2, 3), repeat=d) if norm_squared(c) <= cap)
            selected = tuple(c for c in raw if small_spectral_below(c, 2))
            moments = raw_energy_ball_moments(d, cap)
            self.assertEqual(moments.v0, F(sum(c[0]**2 for c in raw), len(raw)))
            self.assertEqual(moments.m4, F(sum(c[0]**4 for c in raw), len(raw)))
            self.assertEqual(moments.m22, F(sum(c[0]**2*c[1]**2 for c in raw), len(raw)))
            raw_energy_variance = F(sum((norm_squared(c)-d*moments.v0)**2 for c in raw), len(raw))
            self.assertEqual(moments.energy_variance, raw_energy_variance)
            self.assertEqual(moments.variance_coefficient,
                             raw_energy_variance/(d*d)+(1-F(2, d))*moments.m22)
            p = F(len(selected), len(raw))
            v = F(sum(c[0]**2 for c in selected), len(selected))
            for i in range(d):
                for j in range(d):
                    self.assertEqual(F(sum(c[i]*c[j] for c in selected), len(selected)),
                                     v if i == j else 0)
            self.assertLessEqual((v-moments.v0)**2, raw_energy_variance*(1-p)/(p*d*d))
            blocks = (tuple(range(1, d+1)), tuple((-1)**i for i in range(d)))
            t = sum(norm_squared(block) for block in blocks)
            columns = [stacked_image(blocks, tuple(int(i == j) for i in range(d))) for j in range(d)]
            gram = [[sum(x*y for x, y in zip(a, b)) for b in columns] for a in columns]
            gram_square_trace = sum(x*x for row in gram for x in row)
            raw_values = [norm_squared(stacked_image(blocks, c)) for c in raw]
            fourth = F(sum(x*x for x in raw_values), len(raw))
            expected = (moments.m22*((d*t)**2+2*gram_square_trace)
                        +(moments.m4-3*moments.m22)*d*t*t)
            self.assertEqual(fourth, expected)
            chosen = [norm_squared(stacked_image(blocks, c)) for c in selected]
            selected_variance = F(sum((x-v*d*t)**2 for x in chosen), len(selected))
            upper = (moments.variance_coefficient/p-(v-moments.v0)**2)*d*d*t*t
            self.assertLessEqual(selected_variance, upper)
        cube = raw_energy_ball_moments(64, 256)
        self.assertEqual((cube.v0, cube.m4, cube.m22), (F(2), F(34, 5), F(4)))
        self.assertEqual(cube.variance_coefficient, 4-F(26, 320))

    def test_rational_mgf_angles_and_positive_exponential(self):
        self.assertLess(F(707, 500)**2, 2)
        self.assertLess(F(433, 250)**2, 3)
        self.assertLess(F(4619, 5000)**2, F(1707, 2000))
        for tilt in (F(2, 3), F(4, 5), F(1)):
            self.assertTrue(tilted_mgf_certified(tilt))
            z = 1+2*tilt+2*tilt**4
            variance = (2*tilt+8*tilt**4)/z
            for k in range(1, 20):
                raw = (2*tilt+2*tilt**4*4**k)/z
                gaussian = F(factorial(2*k), 2**k*factorial(k))*variance**k
                self.assertLessEqual(raw, gaussian)
        self.assertFalse(tilted_mgf_certified(F(1, 10)))
        self.assertEqual(positive_exponential_lower(F(1), 5), F(163, 60))
        self.assertLess(positive_exponential_lower(F(1), 20), positive_exponential_lower(F(1), 80))
        self.assertLess(positive_exponential_lower(F(1), 80), 3)

    def test_degree_64_profile_and_conditional_statistical_budget(self):
        count = energy_ball_count(64, 104)
        self.assertEqual(count, 20905094450944450994971371210796521612779265)
        bad = energy_ball_rejection_upper(64, 104, 30)
        self.assertLess(bad, F(1, 3))
        lower = bounded_energy_count_lower(64, 104, 30)
        self.assertEqual(lower, 13936729633962967329980914140531014408519511)
        self.assertEqual(lower, 2*count//3+1)
        moments = raw_energy_ball_moments(64, 104)
        self.assertLess(moments.v0, F(25, 16))
        self.assertLess(moments.energy_variance/F(8192), F(1, 256))
        self.assertGreater((9-moments.v0)**2, 24*moments.variance_coefficient)
        self.assertTrue(symmetric_fold_cap_certified(moments, F(2, 3), F(1, 16), F(9), F(1, 16), F(31, 8)))
        self.assertFalse(symmetric_fold_cap_certified(moments, F(2, 3), F(1, 16), F(8), F(1, 16), F(31, 8)))
        q = 4294967197
        profile = bounded_energy_profile(q)
        self.assertEqual(profile["cardinality_lower_bound_inclusive"], lower)
        self.assertEqual(profile["l2_norm_squared_upper_bound"], 104)
        self.assertEqual(profile["operator_norm_strictly_below"], 30)
        self.assertEqual(profile["gamma_squared_over_d_beta_squared"], F(9))
        self.assertTrue(profile["zero_is_included"])
        total = 128*(F(198, lower)+F(7, 2**164)+F(7, q**6)+F(7, q**32)+F(1, 2**160))
        self.assertLess(total, F(1, 2**128))  # statistical components only
        self.assertGreater(F(479, 528)**7, F(1, 2))
        for rank in (0, 1, count//2, count-2, count-1):
            c = energy_ball_unrank(64, 104, rank)
            self.assertLessEqual(norm_squared(c), 104)
            self.assertEqual(energy_ball_rank(c, 104), rank)

    def test_failed_certificates_are_not_positive_or_negative_security_claims(self):
        self.assertGreater(energy_ball_rejection_upper(64, 104, 15), 1)
        with self.assertRaises(ValueError):
            bounded_energy_count_lower(64, 104, 15)
        with self.assertRaises(ValueError):
            bounded_energy_profile(4294967197, coefficient=F(8))
        with self.assertRaises(ValueError):
            bounded_energy_profile(13, degree=2, energy=4, threshold=4)

    def test_strict_input_validation(self):
        for dimension in (-1, True, 2.0, "2"):
            with self.subTest(dimension=dimension), self.assertRaises(ValueError):
                energy_counts(dimension)
        for cap in (-1, True, F(3), 9):
            with self.subTest(cap=cap), self.assertRaises(ValueError):
                energy_ball_count(2, cap)
        for rank in (-1, True, 1.0, 25):
            with self.subTest(rank=rank), self.assertRaises(ValueError):
                energy_ball_unrank(2, 8, rank)
        for c in ((True, 0), (1.0, 0), (3, 0), None):
            with self.subTest(c=c), self.assertRaises(ValueError):
                energy_ball_rank(c, 4)
        with self.assertRaises(ValueError):
            energy_ball_rank((2, 2), 4)
        for degree in (0, 1, 3, True, 64.0):
            with self.subTest(degree=degree), self.assertRaises(ValueError):
                raw_energy_ball_moments(degree, 0)
        for value in (0.8, F(0), F(-1), F(2), True):
            with self.subTest(tilt=value), self.assertRaises(ValueError):
                tilted_mgf_certified(value)
        for threshold in (0, -1, True, 30.0):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                tilted_operator_tail_upper(64, threshold)
        for directions in (0, 7, True, 12.0):
            with self.subTest(directions=directions), self.assertRaises(ValueError):
                tilted_operator_tail_upper(64, 30, directions=directions)
        for terms in (0, -1, True, 80.0):
            with self.subTest(terms=terms), self.assertRaises(ValueError):
                positive_exponential_lower(F(1), terms)
        with self.assertRaises(ValueError):
            positive_exponential_lower(1)
        with self.assertRaises(ValueError):
            tilted_operator_tail_upper(64, 30, F(1, 10))
        for p in (F(0), F(1), 0.5):
            with self.subTest(p=p), self.assertRaises(ValueError):
                bounded_energy_count_lower(64, 104, 30, rejection_upper=p)
        with self.assertRaises(ValueError):
            SymmetricRawMoments(3, F(1), F(1), F(1))
        with self.assertRaises(ValueError):
            SymmetricRawMoments(4, 1, F(1), F(1))
        with self.assertRaises(ValueError):
            SymmetricRawMoments(4, F(2), F(1), F(1))
        with self.assertRaises(ValueError):
            SymmetricRawMoments(4, F(1), F(1), F(2))
        with self.assertRaises(ValueError):
            SymmetricRawMoments(4, F(0), F(1), F(0))
        with self.assertRaises(ValueError):
            symmetric_fold_cap_certified({}, F(2, 3), F(1, 16), F(9), F(1), F(4))
        moments = raw_energy_ball_moments(64, 104)
        for arguments in ((F(1), F(1, 16), F(9), F(1, 16), F(31, 8)),
                          (F(2, 3), F(0), F(9), F(1, 16), F(31, 8)),
                          (F(2, 3), F(1, 16), 9, F(1, 16), F(31, 8)),
                          (F(2, 3), F(1, 16), F(9), F(-1), F(31, 8))):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                symmetric_fold_cap_certified(moments, *arguments)


if __name__ == "__main__":
    unittest.main()
