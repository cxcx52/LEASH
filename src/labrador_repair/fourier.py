"""Certified integer Fourier enclosures for the strict challenge predicate.

An unresolved comparison falls back to exact integer positive definiteness.
Tables are built internally; this API takes no externally supplied certificate.
This module supplies no cryptographic sampler or prover.
"""

from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import factorial

from .challenges import exact_operator_norm_below


def _degree_check(degree):
    if type(degree) is not int or degree < 2 or degree & (degree - 1):
        raise ValueError("degree must be a power of two >=2")


def _positive_integer(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError(name + " must be a positive integer")


def _atan_inverse_interval(denominator, terms):
    """Alternating-series interval for atan(1/denominator), denominator>1."""
    if type(denominator) is not int or denominator <= 1:
        raise ValueError("denominator must be an integer >1")
    _positive_integer(terms, "terms")
    partial = sum((F((-1)**k, (2*k + 1) * denominator**(2*k + 1))
                   for k in range(terms)), F(0))
    next_term = F((-1)**terms, (2*terms + 1) * denominator**(2*terms + 1))
    return min(partial, partial + next_term), max(partial, partial + next_term)


def _certified_pi_interval(terms=24, dyadic_bits=80):
    """Outward dyadic enclosure from pi=16 atan(1/5)-4 atan(1/239)."""
    _positive_integer(dyadic_bits, "dyadic_bits")
    lo5, hi5 = _atan_inverse_interval(5, terms)
    lo239, hi239 = _atan_inverse_interval(239, terms)
    lower, upper = 16*lo5 - 4*hi239, 16*hi5 - 4*lo239
    denominator = 1 << dyadic_bits
    low_integer = lower.numerator * denominator // lower.denominator
    high_integer = -((-upper.numerator * denominator) // upper.denominator)
    result = F(low_integer, denominator), F(high_integer, denominator)
    if not 0 < result[0] <= lower < upper <= result[1] < 4:
        raise ArithmeticError("invalid outward pi enclosure")
    return result


def _taylor_sin_cos(x, terms):
    """Exact rational polynomials with terms powers 0..2K-2 and 1..2K-1."""
    sine = sine_term = x
    cosine = cosine_term = F(1)
    x_squared = x*x
    for k in range(1, terms):
        cosine_term *= -x_squared / ((2*k - 1) * 2*k)
        sine_term *= -x_squared / (2*k * (2*k + 1))
        cosine += cosine_term
        sine += sine_term
    return sine, cosine


def _nearest_integer(value):
    # floor(value+1/2); ties go upward, with error at most 1/2 in either sign.
    return (2*value.numerator + value.denominator) // (2*value.denominator)


@dataclass(frozen=True)
class _CertifiedFourierTable:
    degree: int
    scale: int
    # Entry m represents cos(m*pi/d),sin(m*pi/d), for m modulo 2d.
    twiddles: tuple
    pi_width: F
    polynomial_error_upper: F


@lru_cache(maxsize=16)
def _build_certified_table(degree, bits=40, pi_terms=24, pi_bits=80,
                          taylor_terms=32):
    """Build 2d integer twiddles, each component error strictly below 1/Q.

    A uniform rational Taylor/Lipschitz check proves the approximation error is
    <1/(2Q) before nearest-integer quantization. Inadequate requested precision
    raises ValueError instead of silently weakening the enclosure.
    """
    _degree_check(degree)
    _positive_integer(bits, "bits")
    _positive_integer(taylor_terms, "taylor_terms")
    lower, upper = _certified_pi_interval(pi_terms, pi_bits)
    midpoint, radius = (lower + upper)/2, (upper - lower)/2
    cosine_tail = F(4**(2*taylor_terms), factorial(2*taylor_terms))
    sine_tail = F(4**(2*taylor_terms + 1), factorial(2*taylor_terms + 1))
    polynomial_error = radius + max(cosine_tail, sine_tail)
    scale = 1 << bits
    if not polynomial_error < F(1, 2*scale):
        raise ValueError("requested twiddle approximation is not certified")
    twiddles = []
    for m_mod in range(2*degree):
        m = m_mod if m_mod < degree else m_mod - 2*degree
        sine, cosine = _taylor_sin_cos(F(m, degree)*midpoint, taylor_terms)
        twiddles.append((_nearest_integer(scale*cosine),
                         _nearest_integer(scale*sine)))
    return _CertifiedFourierTable(degree, scale, tuple(twiddles),
                                 upper - lower, polynomial_error)


def _table_operator_norm_below(coefficients, threshold, table, with_path=False):
    """Exact strict norm predicate: certified accept/reject, else integer SPD.

    ``table`` must be obtained from ``_build_certified_table``; its mathematical
    certificate is part of this internal prototype's trusted implementation.
    Returning the path is for deterministic validation and performance reporting.
    """
    coefficients = tuple(coefficients)
    _positive_integer(threshold, "threshold")
    if len(coefficients) != table.degree:
        raise ValueError("coefficient and table degrees differ")
    if any(type(c) is not int or not -2 <= c <= 2 for c in coefficients):
        raise ValueError("coefficients must be integers in {-2,-1,0,1,2}")
    degree, scale = table.degree, table.scale
    error = sum(abs(c) for c in coefficients)
    threshold_squared = threshold*threshold*scale*scale
    all_upper_bounds_pass = True
    for k in range(degree//2):
        root = 2*k + 1
        real = imaginary = 0
        for j, coefficient in enumerate(coefficients):
            cosine, sine = table.twiddles[(root*j) % (2*degree)]
            real += coefficient*cosine
            imaginary += coefficient*sine
        lower_real = max(abs(real) - error, 0)
        lower_imaginary = max(abs(imaginary) - error, 0)
        lower_squared = lower_real**2 + lower_imaginary**2
        if lower_squared >= threshold_squared:
            return (False, "interval_reject") if with_path else False
        upper_squared = (abs(real) + error)**2 + (abs(imaginary) + error)**2
        if upper_squared >= threshold_squared:
            all_upper_bounds_pass = False
    if all_upper_bounds_pass:
        return (True, "interval_accept") if with_path else True
    answer = exact_operator_norm_below(coefficients, threshold)
    return (answer, "exact_fallback") if with_path else answer



def certified_operator_norm_below(coefficients, threshold, *, bits=40,
                                   with_path=False):
    """Decide exactly whether the negacyclic multiplication norm is <threshold.

    The internally cached table is certified using integer/rational arithmetic.
    ``bits`` controls enclosure precision, never the accepted mathematical set;
    inadequate precision settings raise ValueError. With ``with_path=True``,
    return (decision, path), where the path identifies interval acceptance,
    interval rejection, or exact fallback. This is a diagnostic, not a security
    or sampling-probability estimate. Equality always rejects.
    """
    coefficients = tuple(coefficients)
    _degree_check(len(coefficients))
    _positive_integer(threshold, "threshold")
    _positive_integer(bits, "bits")
    if any(type(c) is not int or not -2 <= c <= 2 for c in coefficients):
        raise ValueError("coefficients must be integers in {-2,-1,0,1,2}")
    table = _build_certified_table(len(coefficients), bits=bits)
    return _table_operator_norm_below(coefficients, threshold, table, with_path)
