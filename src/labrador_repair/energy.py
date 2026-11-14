"""Exact bounded-energy challenge and symmetric-moment certificates.

This module counts finite sets, decodes integer ranks, and checks sufficient
rational inequalities. It supplies no RNG, prover, or MSIS security estimate.
The optional profile uses energy <=104, operator norm <30, and degree 64.
"""

from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache

from .bounds import validate_ring
from .challenges import _validate_degree
from .fourier import certified_operator_norm_below


_SYMBOLS = (-2, -1, 0, 1, 2)
_ANGLE_LOWER = {8: F(1707, 2000), 12: F(933, 1000), 16: F(9619, 10000)}


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def _energy_parameters(dimension, energy):
    _integer(dimension, "dimension")
    _integer(energy, "energy")
    if energy > 4*dimension:
        raise ValueError("energy must be at most four times dimension")


def _fraction(value, name, *, positive=False):
    if not isinstance(value, F) or value < 0 or (positive and value == 0):
        raise ValueError(name + " must be a " + ("positive" if positive else "nonnegative") + " Fraction")


def _probability(value, name):
    _fraction(value, name, positive=True)
    if value >= 1:
        raise ValueError(name + " must be strictly below one")


def _coefficients(values):
    try:
        values = tuple(values)
    except TypeError as exc:
        raise ValueError("coefficients must be an iterable of integer symbols") from exc
    if any(type(c) is not int or c not in _SYMBOLS for c in values):
        raise ValueError("coefficients must be integers in {-2,-1,0,1,2}")
    return values


@lru_cache(maxsize=256)
def _counts(dimension):
    counts = [1]
    for _ in range(dimension):
        updated = [0]*(len(counts)+4)
        for energy, count in enumerate(counts):
            updated[energy] += count
            updated[energy+1] += 2*count
            updated[energy+4] += 2*count
        counts = updated
    return tuple(counts)


def energy_counts(dimension):
    """Coefficients of (1+2z+2z^4)^dimension; dimension may be zero.

    This combinatorial API allows all nonnegative integer dimensions. Ring and
    moment APIs below additionally require a power-of-two degree >=2.
    """
    _integer(dimension, "dimension")
    return _counts(dimension)


def _ball_count(dimension, budget):
    return sum(_counts(dimension)[:min(budget, 4*dimension)+1]) if budget >= 0 else 0


def energy_ball_count(dimension, energy):
    """Exact number of five-symbol vectors with squared norm <=energy."""
    _energy_parameters(dimension, energy)
    return _ball_count(dimension, energy)


def energy_shell_count(dimension, energy):
    """Exact number of vectors with squared norm equal to energy (possibly 0)."""
    _energy_parameters(dimension, energy)
    return _counts(dimension)[energy]


def energy_ball_unrank(dimension, energy, rank):
    """Decode a zero-based lexicographic rank; no random sampling is performed."""
    count = energy_ball_count(dimension, energy)
    _integer(rank, "rank")
    if rank >= count:
        raise ValueError("rank must be smaller than the exact ball count")
    result = []
    budget = energy
    for remaining in range(dimension-1, -1, -1):
        for symbol in _SYMBOLS:
            completions = _ball_count(remaining, budget-symbol*symbol)
            if rank < completions:
                result.append(symbol)
                budget -= symbol*symbol
                break
            rank -= completions
        else:
            raise ArithmeticError("rank decoder exhausted a valid count")
    return tuple(result)


def energy_ball_rank(coefficients, energy):
    """Inverse of energy_ball_unrank for a valid bounded-energy vector."""
    coefficients = _coefficients(coefficients)
    _energy_parameters(len(coefficients), energy)
    if sum(c*c for c in coefficients) > energy:
        raise ValueError("coefficient vector exceeds the energy cap")
    rank, budget = 0, energy
    for position, actual in enumerate(coefficients):
        remaining = len(coefficients)-position-1
        rank += sum(_ball_count(remaining, budget-symbol*symbol)
                    for symbol in _SYMBOLS if symbol < actual)
        budget -= actual*actual
    return rank


def bounded_energy_member(coefficients, energy, threshold):
    """Exact ball/strict-operator membership using the existing Fourier/SPD API."""
    coefficients = _coefficients(coefficients)
    _validate_degree(len(coefficients))
    _energy_parameters(len(coefficients), energy)
    _integer(threshold, "threshold", 1)
    if sum(c*c for c in coefficients) > energy:
        return False
    return certified_operator_norm_below(coefficients, threshold)


def _tilted_parameters(tilt):
    _fraction(tilt, "tilt", positive=True)
    if tilt > 1:
        raise ValueError("tilt must be at most one")
    normalizer = 1+2*tilt+2*tilt**4
    variance = (2*tilt+8*tilt**4)/normalizer
    fourth = (2*tilt+32*tilt**4)/normalizer
    return normalizer, variance, fourth


def tilted_mgf_certified(tilt):
    """Check a sufficient E exp(tX)<=exp(v*t^2/2) moment comparison.

    The tilted symbol law has weights tilt^(c^2). False means this sufficient
    comparison failed; it is not a negative claim about every possible MGF bound.
    """
    _, variance, fourth = _tilted_parameters(tilt)
    return fourth <= 3*variance*variance and 5*variance > 4


def positive_exponential_lower(value, terms=80):
    """Strict rational lower bound sum_{k=0}^terms value^k/k! < exp(value)."""
    _fraction(value, "value", positive=True)
    _integer(terms, "terms", 1)
    term = total = F(1)
    for k in range(1, terms+1):
        term *= value/k
        total += term
    return total


def tilted_operator_tail_upper(degree, threshold, tilt=F(4, 5), *,
                               directions=12, taylor_terms=80):
    """Strict rational upper bound on tilted-product operator rejection.

    Values >=1 are vacuous certificates. Directions are one of 8,12,16 with
    proved rational cosine constants. No floating-point decision is used.
    """
    _validate_degree(degree)
    _integer(threshold, "threshold", 1)
    _integer(directions, "directions", 1)
    if directions not in _ANGLE_LOWER:
        raise ValueError("directions must be one of 8,12,16")
    _integer(taylor_terms, "taylor_terms", 1)
    _, variance, fourth = _tilted_parameters(tilt)
    if not (fourth <= 3*variance*variance and 5*variance > 4):
        raise ValueError("the sufficient tilted MGF certificate did not pass")
    exponent = _ANGLE_LOWER[directions]*threshold**2/(degree*variance)
    return F(degree*directions, 2)/positive_exponential_lower(exponent, taylor_terms)


def energy_ball_rejection_upper(degree, energy, threshold, tilt=F(4, 5), *,
                                directions=12, taylor_terms=80):
    """Strict upper bound for a UNIFORM raw ball's operator rejection.

    Uses |bad ball|<=Z^d*tilt^(-energy)*P_tilt(bad), then divides by the exact
    ball count. It does not treat the conditioned tilted ball as uniform.
    """
    _validate_degree(degree)
    count = energy_ball_count(degree, energy)
    normalizer, _, _ = _tilted_parameters(tilt)
    tail = tilted_operator_tail_upper(degree, threshold, tilt,
                                     directions=directions, taylor_terms=taylor_terms)
    return normalizer**degree/(tilt**energy*count)*tail


def bounded_energy_count_lower(degree, energy, threshold, tilt=F(4, 5), *,
                               rejection_upper=F(1, 3), directions=12,
                               taylor_terms=80):
    """Inclusive cardinality lower bound, conditional on the checked tail bound."""
    _probability(rejection_upper, "rejection_upper")
    bound = energy_ball_rejection_upper(degree, energy, threshold, tilt,
                                       directions=directions, taylor_terms=taylor_terms)
    if bound > rejection_upper:
        raise ValueError("the requested sufficient rejection certificate did not pass")
    lower = (1-rejection_upper)*energy_ball_count(degree, energy)
    return lower.numerator//lower.denominator+1


@dataclass(frozen=True)
class SymmetricRawMoments:
    """Moment algebra for an assumed signed-permutation-invariant raw law.

    Validation checks necessary moment consistency, not existence of a law with
    arbitrary supplied moments. raw_energy_ball_moments derives actual moments
    from exact counts. The ring degree must be a power of two >=2.
    """
    degree: int
    v0: F
    m4: F
    m22: F

    def __post_init__(self):
        _validate_degree(self.degree)
        for name in ("v0", "m4", "m22"):
            _fraction(getattr(self, name), name)
        if (self.m4 < self.v0*self.v0 or self.m22 > self.m4
                or self.energy_variance < 0
                or (self.v0 == 0 and (self.m4 != 0 or self.m22 != 0))):
            raise ValueError("moments violate a necessary variance inequality")

    @property
    def energy_variance(self):
        d = self.degree
        return d*self.m4+d*(d-1)*self.m22-d*d*self.v0*self.v0

    @property
    def variance_coefficient(self):
        d = self.degree
        # Equivalent to 2*m22-v0^2+(m4-3*m22)/d; nonnegative for actual moments.
        return self.energy_variance/(d*d)+(1-F(2, d))*self.m22


def raw_energy_ball_moments(degree, energy):
    """Exact raw uniform-ball v0,m4,m22, with dependent coordinate magnitudes."""
    _validate_degree(degree)
    count = energy_ball_count(degree, energy)
    coefficients = _counts(degree)
    mean_energy = F(sum(e*coefficients[e] for e in range(energy+1)), count)
    second_energy = F(sum(e*e*coefficients[e] for e in range(energy+1)), count)
    m4 = F(2*_ball_count(degree-1, energy-1)+32*_ball_count(degree-1, energy-4), count)
    m22 = (second_energy-degree*m4)/(degree*(degree-1))
    return SymmetricRawMoments(degree, mean_energy/degree, m4, m22)


def symmetric_fold_cap_certified(moments, acceptance_lower, failure_upper,
                                  coefficient, rho_upper, sqrt_odds_upper):
    """Sufficient general centered moment cap, not a distribution certificate.

    Requires the stated raw law, filter isotropy, actual acceptance p>a, and
    fixed witnesses before independent selected challenges. Checks Gamma^2=
    coefficient*d*beta^2 with explicit rational upper bounds on both radicals.
    """
    if not isinstance(moments, SymmetricRawMoments):
        raise ValueError("moments must be a SymmetricRawMoments instance")
    _probability(acceptance_lower, "acceptance_lower")
    _probability(failure_upper, "failure_upper")
    _fraction(coefficient, "coefficient", positive=True)
    _fraction(rho_upper, "rho_upper")
    _fraction(sqrt_odds_upper, "sqrt_odds_upper")
    a, f, d = acceptance_lower, failure_upper, moments.degree
    rho_squared = moments.energy_variance*(1-a)/(a*d*d)
    margin = coefficient-moments.v0
    return (rho_upper**2 >= rho_squared and sqrt_odds_upper**2 >= (1-f)/f
            and margin >= 0 and margin**2 >= moments.variance_coefficient/(a*f)
            and coefficient >= (moments.v0+rho_upper)*(1+sqrt_odds_upper))


def bounded_energy_profile(q, degree=64, energy=104, threshold=30, *,
                            tilt=F(4, 5), rejection_upper=F(1, 3),
                            failure_upper=F(1, 16), coefficient=F(9),
                            rho_upper=F(1, 16), sqrt_odds_upper=F(31, 8),
                            directions=12, taylor_terms=80):
    """Link exact bounded-energy count and honest-fold certificates.

    Returns only mathematical parameter certificates. It does not establish a
    recursive schedule, numerical MSIS hardness, or full knowledge security.
    """
    _validate_degree(degree)
    _integer(q, "q", 3)
    validate_ring(q, degree, radius=2)
    count_lower = bounded_energy_count_lower(
        degree, energy, threshold, tilt, rejection_upper=rejection_upper,
        directions=directions, taylor_terms=taylor_terms)
    moments = raw_energy_ball_moments(degree, energy)
    a = 1-rejection_upper
    if not symmetric_fold_cap_certified(moments, a, failure_upper, coefficient,
                                        rho_upper, sqrt_odds_upper):
        raise ValueError("the requested sufficient honest-fold certificate did not pass")
    return {
        "scope": "Challenge/count/honest-fold certificate only; not full security",
        "degree": degree, "q": q,
        "raw_ball_cardinality_exact": energy_ball_count(degree, energy),
        "cardinality_lower_bound_inclusive": count_lower,
        "filtered_cardinality_is_not_enumerated": True,
        "l2_norm_squared_upper_bound": energy,
        "operator_norm_strictly_below": threshold,
        "acceptance_probability_strictly_greater_than": a,
        "expected_raw_ball_draws_strictly_less_than": 1/a,
        "tilt_used_for_count_certificate": tilt,
        "angular_directions": directions,
        "positive_exponential_Taylor_degree": taylor_terms,
        "zero_is_included": True,
        "independent_zero_draw_probability": "exactly 1/|C|",
        "unit_difference_ring_condition_checked": True,
        "raw_moments": {"v0": moments.v0, "m4": moments.m4, "m22": moments.m22,
                        "energy_variance": moments.energy_variance,
                        "variance_coefficient_g": moments.variance_coefficient},
        "gamma_squared_over_d_beta_squared": coefficient,
        "honest_fold_rejection_probability_upper": failure_upper,
        "required_chronology": "Fix all s_i before drawing independent filtered challenges",
        "required_witness_energy": "sum_i ||s_i||^2 <= beta^2",
    }
