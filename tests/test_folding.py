"""Exact moment identities and parameter certificates, including stacked outputs."""

from fractions import Fraction as F
from itertools import product
import unittest

from labrador_repair.folding import (
    centered_fold_cap_certified, elementary_fold_cap_certified,
    filtered_folding_profile, paired_fold_cap_certified,
)
from labrador_repair.ring import negacyclic_multiply


def energy(vector):
    return sum(x*x for x in vector)


def output(blocks, coefficients):
    return tuple(x for block in blocks for x in negacyclic_multiply(block, coefficients))


def moments(vectors):
    return (F(sum(energy(v) for v in vectors), len(vectors)),
            F(sum(energy(v)**2 for v in vectors), len(vectors)))


def small_filter(coefficients, threshold):
    # Independent closed spectral formulas; no Fourier or SPD predicate is used.
    if len(coefficients) == 2:
        return energy(coefficients) < threshold*threshold
    c = coefficients
    cross = c[0]*c[1]+c[1]*c[2]+c[2]*c[3]-c[0]*c[3]
    margin = threshold*threshold-energy(c)
    return margin > 0 and margin*margin > 2*cross*cross


class FoldingMoments(unittest.TestCase):
    def test_raw_fourth_moment_and_stacked_complex_structure(self):
        for blocks in (((1, 2), (-1, 1)), ((1, -2, 0, 1), (0, 1, 1, 0))):
            d = len(blocks[0])
            columns = [output(blocks, tuple(int(k == j) for k in range(d)))
                       for j in range(d)]
            gram = [[sum(x*y for x, y in zip(a, b)) for b in columns] for a in columns]
            t = sum(energy(block) for block in blocks)
            gram_trace = sum(gram[j][j] for j in range(d))
            gram_squared = sum(x*x for row in gram for x in row)
            self.assertEqual(gram_trace, d*t)
            self.assertTrue(all(gram[j][j] == t for j in range(d)))
            self.assertLessEqual(gram_squared, F(gram_trace**2, 2))
            j_poly = tuple(int(k == d//2) for k in range(d))
            for basis_index in range(d):
                basis = tuple(int(k == basis_index) for k in range(d))
                shifted_input = negacyclic_multiply(j_poly, basis)
                original_output = output(blocks, basis)
                shifted_output = tuple(x for start in range(0, len(original_output), d)
                                       for x in negacyclic_multiply(j_poly, original_output[start:start+d]))
                self.assertEqual(output(blocks, shifted_input), shifted_output)
            raw = [output(blocks, c) for c in product(range(-2, 3), repeat=d)]
            second, fourth = moments(raw)
            expected = 4*gram_trace**2+8*gram_squared-F(26, 5)*d*t*t
            self.assertEqual(second, 2*d*t)
            self.assertEqual(fourth, expected)
            upper = d*d*(8-F(26, 5*d))*t*t
            self.assertLessEqual(fourth, upper)
            if d == 2:
                self.assertEqual(fourth, upper)

    def test_filtered_joint_moments_with_independent_small_spectra(self):
        for left, right in ((((1, 2), (-1, 1)), ((0, 1), (2, -1))),
                            (((1, -2, 0, 1), (0, 1, 1, 0)), ((2, 0, -1, 1), (-1, 0, 1, 2)))):
            d = len(left[0])
            cube = tuple(product(range(-2, 3), repeat=d))
            selected = tuple(c for c in cube if small_filter(c, 2))
            p = F(len(selected), len(cube))
            v = F(sum(c[0]**2 for c in selected), len(selected))
            for i in range(d):
                self.assertEqual(sum(c[i] for c in selected), 0)
                for j in range(d):
                    self.assertEqual(F(sum(c[i]*c[j] for c in selected), len(selected)),
                                     v if i == j else 0)
            self.assertLessEqual((v-2)**2, F(14, 5*d)*(1-p)/p)
            ys = [output(left, c) for c in selected]
            zs = [output(right, c) for c in selected]
            mu_y, nu_y = moments(ys)
            mu_z, nu_z = moments(zs)
            pair_count = len(selected)**2
            inner_squared = F(sum(sum(x*y for x, y in zip(yv, zv))**2
                                  for yv in ys for zv in zs), pair_count)
            self.assertLessEqual(inner_squared, mu_y*mu_z/2)
            combined = [tuple(x+y for x, y in zip(yv, zv)) for yv in ys for zv in zs]
            mu, nu = moments(combined)
            self.assertEqual(mu, mu_y+mu_z)
            self.assertEqual(nu, nu_y+nu_z+2*mu_y*mu_z+4*inner_squared)
            t_left, t_right = sum(energy(b) for b in left), sum(energy(b) for b in right)
            g = 4-F(26, 5*d)
            for second, fourth, t in ((mu_y, nu_y, t_left), (mu_z, nu_z, t_right)):
                self.assertEqual(second, v*d*t)
                self.assertLessEqual(fourth-second**2, d*d*t*t*(g/p-(v-2)**2))
            centered = d*d*(v*v*(t_left+t_right)**2
                             +(g/p-(v-2)**2-v*v)*(t_left*t_left+t_right*t_right))
            self.assertLessEqual(nu-mu*mu, centered)

    def test_exact_profile_and_two_independent_baselines(self):
        a, f = F(901, 1024), F(1, 16)
        self.assertTrue(elementary_fold_cap_certified(64, a, f, F(18)))
        self.assertFalse(elementary_fold_cap_certified(64, a, f, F(17)))
        self.assertTrue(paired_fold_cap_certified(64, a, f, F(12)))
        self.assertFalse(paired_fold_cap_certified(64, a, f, F(1199, 100)))
        self.assertTrue(centered_fold_cap_certified(64, a, f, F(21, 2), F(1, 12), F(31, 8)))
        self.assertFalse(centered_fold_cap_certified(64, a, f, F(10), F(1, 12), F(31, 8)))
        profile = filtered_folding_profile(4294967197)
        self.assertEqual(profile["gamma_squared_over_d_beta_squared"], F(21, 2))
        self.assertEqual(profile["conditional_mean_shift_squared_upper"], F(861, 144160))
        self.assertEqual(profile["raw_variance_coefficient_g"], F(627, 160))
        self.assertEqual(profile["challenge_certificate"]["operator_norm_strictly_below"], 34)
        self.assertEqual(profile["challenge_certificate"]["cardinality_lower_bound_inclusive"],
                         901*5**64//1024+1)
        with self.assertRaises(ValueError):
            filtered_folding_profile(4294967197, threshold=31)

    def test_certificate_boundaries_and_invalid_radical_witnesses(self):
        self.assertTrue(paired_fold_cap_certified(2, F(1, 2), F(1, 2), F(8)))
        self.assertFalse(paired_fold_cap_certified(2, F(1, 2), F(1, 2), F(799, 100)))
        args = (2, F(1, 2), F(1, 2))
        self.assertTrue(centered_fold_cap_certified(*args, F(7), F(3, 2), F(1)))
        self.assertFalse(centered_fold_cap_certified(*args, F(699, 100), F(3, 2), F(1)))
        args = (64, F(901, 1024), F(1, 16), F(21, 2))
        self.assertFalse(centered_fold_cap_certified(*args, F(1, 100), F(31, 8)))
        self.assertFalse(centered_fold_cap_certified(*args, F(1, 12), F(3)))
        for degree in (1, 3, True, 64.0):
            with self.assertRaises(ValueError):
                paired_fold_cap_certified(degree, F(1, 2), F(1, 16), F(18))
        for acceptance in (F(0), F(1), 0.5):
            with self.assertRaises(ValueError):
                paired_fold_cap_certified(64, acceptance, F(1, 16), F(18))
        with self.assertRaises(ValueError):
            centered_fold_cap_certified(*args, 0.1, F(31, 8))


if __name__ == "__main__":
    unittest.main()
