"""Exact arithmetic checks for certified filtered cubical challenges.

No prover, cryptographic RNG, FFT, floating-point decision, or attack is implemented.
The operator predicate is a reference certificate checker, not optimized production code.
"""
from fractions import Fraction
from itertools import product
from math import factorial, isqrt
import json


def power_of_two(n):
    return isinstance(n, int) and n >= 2 and n & (n - 1) == 0


def tail_certificate(d, threshold, rejection_numerator=1, rejection_denominator=2):
    """Certify 4*d*exp(-17*T*T/(40*d)) < rejection_numerator/denominator.

    Uses e > 163/60, not a numerical exponential approximation.
    """
    assert power_of_two(d) and isinstance(threshold, int) and threshold > 0
    u, v = rejection_numerator, rejection_denominator
    assert 0 < u < v
    a, b = 17 * threshold * threshold, 40 * d
    return (4*d*v)**b * 60**a < u**b * 163**a


def first_certified_threshold(d):
    for threshold in range(1, 2*d+1):
        if tail_certificate(d, threshold):
            return threshold
    raise AssertionError("Expected a threshold before the deterministic 2d norm bound")


def certified_count_lower(d, threshold, rejection_numerator=1, rejection_denominator=2):
    assert tail_certificate(d, threshold, rejection_numerator, rejection_denominator)
    # N > (1-u/v)*5**d, so floor(rhs)+1 is an inclusive integer lower bound.
    return ((rejection_denominator-rejection_numerator)*5**d)//rejection_denominator+1


def negacyclic_matrix(coefficients):
    d = len(coefficients)
    assert power_of_two(d)
    matrix = [[0]*d for _ in range(d)]
    for col in range(d):
        for j, value in enumerate(coefficients):
            row = j + col
            if row < d:
                matrix[row][col] = value
            else:
                matrix[row-d][col] = -value
    return matrix


def positive_definite_integer(matrix):
    """Strict SPD check by Sylvester and exact fraction-free Bareiss pivots.

    Every returned True is backed by positivity of all leading principal minors.
    Zero pivots reject, which is necessary for an equality boundary.
    """
    n = len(matrix)
    assert all(len(row) == n for row in matrix)
    assert all(matrix[i][j] == matrix[j][i] for i in range(n) for j in range(n))
    a = [row[:] for row in matrix]
    previous = 1
    for k in range(n):
        pivot = a[k][k]
        if pivot <= 0:
            return False
        if k == n-1:
            return True
        for i in range(k+1, n):
            for j in range(k+1, n):
                numerator = pivot*a[i][j]-a[i][k]*a[k][j]
                quotient, remainder = divmod(numerator, previous)
                assert remainder == 0, "Bareiss exact division failed"
                a[i][j] = quotient
        for i in range(k+1, n):
            a[i][k] = 0
            a[k][i] = 0
        previous = pivot
    return True


def certified_op_below(coefficients, threshold):
    """Decide ||multiplication_by_c||_op < threshold using integers only."""
    assert power_of_two(len(coefficients))
    assert isinstance(threshold, int) and threshold > 0
    assert all(isinstance(x, int) and -2 <= x <= 2 for x in coefficients)
    a = negacyclic_matrix(coefficients)
    d = len(a)
    gram_gap = [[(threshold*threshold if i == j else 0)
                 -sum(a[k][i]*a[k][j] for k in range(d))
                 for j in range(d)] for i in range(d)]
    return positive_definite_integer(gram_gap)


def prime_by_trial_division(q):
    if q < 2:
        return False
    if q % 2 == 0:
        return q == 2
    return all(q % k for k in range(3, isqrt(q)+1, 2))


def unit_cube_parameter_certificate(d, q):
    assert power_of_two(d)
    assert prime_by_trial_division(q)
    assert q > 32 and q % 8 == 5
    # Frobenius orbit size of primitive 2d-th roots.
    order = d//2
    assert pow(q, order, 2*d) == 1
    if order > 1:
        assert pow(q, order//2, 2*d) != 1
    return True


def determinant_mod(matrix, q):
    a = [[x % q for x in row] for row in matrix]
    result = 1
    for k in range(len(a)):
        pivot_row = next((i for i in range(k, len(a)) if a[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            result = -result
        pivot = a[k][k]
        result = result*pivot % q
        inverse = pow(pivot, -1, q)
        for i in range(k+1, len(a)):
            factor = a[i][k]*inverse % q
            for j in range(k+1, len(a)):
                a[i][j] = (a[i][j]-factor*a[k][j]) % q
    return result % q


def guaranteed_error_bits(probability):
    assert 0 < probability <= 1
    return (probability.denominator//probability.numerator).bit_length()-1


def checks():
    assert sum(Fraction(1, factorial(k)) for k in range(6)) == Fraction(163, 60)
    assert 2 > Fraction(49, 25)  # sqrt(2)>7/5, hence cos^2(pi/8)>17/20.
    for k in range(1, 101):
        assert Fraction(2+2*4**k, 5) <= Fraction(factorial(2*k), factorial(k))

    degrees = [2, 4, 8, 16, 32, 64, 128, 256]
    thresholds = {d: first_certified_threshold(d) for d in degrees}
    assert thresholds[64] == 31
    assert not tail_certificate(64, 30)
    assert tail_certificate(64, 31)
    assert tail_certificate(64, 31, 7, 16)

    # Independent closed-form spectral checks in dimensions 2 and 4.
    d2_cases = 0
    for c in product(range(-2, 3), repeat=2):
        for t in range(1, 5):
            assert certified_op_below(c, t) == (sum(x*x for x in c) < t*t)
            d2_cases += 1
    d4_cases = 0
    accepted_d4_t4 = 0
    for c in product(range(-2, 3), repeat=4):
        energy = sum(x*x for x in c)
        cross = c[0]*c[1]+c[1]*c[2]+c[2]*c[3]-c[0]*c[3]
        for t in range(1, 7):
            margin = t*t-energy
            exact_spectral = margin > 0 and margin*margin > 2*cross*cross
            answer = certified_op_below(c, t)
            assert answer == exact_spectral
            d4_cases += 1
            if t == 4 and answer:
                accepted_d4_t4 += 1

    # Equality is rejected: c=2 has operator norm exactly 2.
    assert not certified_op_below([2]+[0]*63, 2)
    assert certified_op_below([2]+[0]*63, 31)
    assert certified_op_below([0]*64, 31)
    assert not certified_op_below([2]*64, 31)

    unit_cube_parameter_certificate(64, 4294967197)
    unit_cube_parameter_certificate(4, 37)
    unit_cases = 0
    for f in product(range(-4, 5), repeat=4):
        if any(f):
            assert determinant_mod(negacyclic_matrix(f), 37) != 0
            unit_cases += 1
    # Without the modulus-size hypothesis a nonzero short difference can fail.
    assert determinant_mod(negacyclic_matrix([2, 3]), 13) == 0

    d, t = 64, 31
    lower_half = certified_count_lower(d, t)
    lower_stronger = certified_count_lower(d, t, 7, 16)
    row_counts = [112, 33, 15, 8, 7, 5, 4]
    one_layer = Fraction(112+2, lower_half)
    all_layers = Fraction(sum(r+2 for r in row_counts), lower_half)
    return {
        "moment_checks": 100,
        "first_integer_thresholds_under_this_certificate": thresholds,
        "d64_T": 31,
        "d64_raw_candidates": str(5**64),
        "d64_count_lower_from_half_acceptance": str(lower_half),
        "d64_count_lower_from_nine_sixteenths_acceptance": str(lower_stronger),
        "d64_acceptance_lower_strict": "9/16",
        "d64_expected_candidate_draws_upper_strict": "16/9",
        "d64_coefficient_norm_squared_upper": 256,
        "example_modulus_prime": 4294967197,
        "d2_exact_spectral_cases": d2_cases,
        "d4_exact_spectral_cases": d4_cases,
        "d4_T4_exact_count": accepted_d4_t4,
        "d4_q37_unit_difference_cases": unit_cases,
        "single_layer_r112_challenge_error_guaranteed_bits": guaranteed_error_bits(one_layer),
        "seven_layer_paper_multiplicities_challenge_only_guaranteed_bits": guaranteed_error_bits(all_layers),
        "note": "These are challenge-term certificates, not end-to-end security estimates."
    }


if __name__ == "__main__":
    print(json.dumps(checks(), indent=2))
