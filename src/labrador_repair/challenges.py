"""Optional, certified operator-norm-filtered five-symbol challenge family.

This module certifies mathematical cardinality bounds and exact norm predicates.
It does not replace ``bounds.challenge_cube``, provide a production CSPRNG, or
implement a cryptographic prover. All decisions use integer/rational arithmetic.
"""

from fractions import Fraction

from .bounds import validate_ring
from .ring import negacyclic_multiply


def _validate_degree(degree):
    if type(degree) is not int or degree < 2 or degree & (degree - 1):
        raise ValueError("degree must be a power of two >=2")


def _validate_threshold(threshold):
    if type(threshold) is not int or threshold <= 0:
        raise ValueError("threshold must be a positive integer")


def _validate_rejection_bound(rejection_upper):
    if not isinstance(rejection_upper, Fraction) or not 0 < rejection_upper < 1:
        raise ValueError("rejection_upper must be a Fraction strictly between 0 and 1")


def filtered_tail_certified(degree, threshold, rejection_upper=Fraction(1, 2)):
    """Certify Pr[raw operator norm >= threshold] < rejection_upper.

    Raw coefficients are independent uniform symbols in {-2,-1,0,1,2}.
    The proof bounds rejection by 4*d*exp(-17*T*T/(40*d)), then uses
    e>163/60. A False result means this sufficient certificate did not pass;
    it does not assert a lower bound on actual rejection probability.
    """
    _validate_degree(degree)
    _validate_threshold(threshold)
    _validate_rejection_bound(rejection_upper)
    numerator = rejection_upper.numerator
    denominator = rejection_upper.denominator
    exponent = 17 * threshold * threshold
    power = 40 * degree
    return ((4 * degree * denominator)**power * 60**exponent
            < numerator**power * 163**exponent)


def filtered_challenge_count_lower(degree, threshold,
                                   rejection_upper=Fraction(1, 2)):
    """Return an inclusive integer lower bound on the filtered cardinality.

    The set contains exactly the raw cube polynomials with operator norm <T.
    The returned integer is a certified lower bound, NOT its exact cardinality.
    Raise ValueError when the requested sufficient tail certificate does not pass.
    """
    if not filtered_tail_certified(degree, threshold, rejection_upper):
        raise ValueError("the requested sufficient rejection certificate did not pass")
    accepted_lower = 1 - rejection_upper
    return (accepted_lower.numerator * 5**degree
            // accepted_lower.denominator) + 1


def _positive_definite_integer(matrix):
    """Strict Sylvester test via fraction-free Bareiss principal minors."""
    a = [row[:] for row in matrix]
    previous = 1
    for k in range(len(a)):
        pivot = a[k][k]
        if pivot <= 0:
            return False
        if k == len(a) - 1:
            return True
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                numerator = pivot * a[i][j] - a[i][k] * a[k][j]
                quotient, remainder = divmod(numerator, previous)
                if remainder:
                    raise ArithmeticError("Bareiss principal-minor division was not exact")
                a[i][j] = quotient
        for i in range(k + 1, len(a)):
            a[i][k] = 0
            a[k][i] = 0
        previous = pivot
    return True


def exact_operator_norm_below(coefficients, threshold):
    """Decide ||multiplication_by_c||_op < threshold exactly.

    Coefficients must form a five-symbol cube polynomial of power-of-two degree.
    This is an exact reference predicate, not an optimized sampler. It forms
    T^2 I-A_c^T A_c using the existing negacyclic ring operation and checks all
    leading principal minors. Equality rejects; no FFT tolerance is involved.
    """
    coefficients = tuple(coefficients)
    degree = len(coefficients)
    _validate_degree(degree)
    _validate_threshold(threshold)
    if any(type(value) is not int or not -2 <= value <= 2
           for value in coefficients):
        raise ValueError("coefficients must be integers in {-2,-1,0,1,2}")
    columns = [negacyclic_multiply(coefficients,
                                  tuple(int(i == j) for i in range(degree)))
               for j in range(degree)]
    gram_gap = [[(threshold**2 if i == j else 0)
                 - sum(x * y for x, y in zip(columns[i], columns[j]))
                 for j in range(degree)] for i in range(degree)]
    return _positive_definite_integer(gram_gap)


def filtered_challenge_profile(q, degree=64, threshold=31,
                               rejection_upper=Fraction(7, 16)):
    """An optional statistical challenge certificate; not a security estimate.

    ``validate_ring`` supplies the existing LS18 q=5 mod8, q>32 unit-difference
    condition for radius two. Its primality checker is intended for small example
    moduli. This function does not certify MSIS hardness or protocol parameters.
    """
    lower = filtered_challenge_count_lower(degree, threshold, rejection_upper)
    validate_ring(q, degree=degree, radius=2)
    acceptance_lower = 1 - rejection_upper
    return {
        "family": "Optional operator-norm-filtered five-symbol cube",
        "scope": "Statistical challenge certificate only; not full security",
        "q": q,
        "degree": degree,
        "operator_norm_strictly_below": threshold,
        "cardinality_lower_bound_inclusive": lower,
        "cardinality_is_not_enumerated": True,
        "acceptance_probability_strictly_greater_than": acceptance_lower,
        "expected_candidate_draws_strictly_less_than": 1 / acceptance_lower,
        "l2_norm_squared_upper_bound": 4 * degree,
        "difference_linf_upper_bound": 4,
        "unit_difference_ring_condition_checked": True,
        "zero_is_included": True,
        "independent_zero_draw_probability": "exactly 1/|C|",
    }
