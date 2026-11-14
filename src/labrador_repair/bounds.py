"""Rational certificates for the corrected 1024-row modular JL lemma.

These certificates verify numerical steps of the proof in docs/. They do not
replace the proof, certify Module-SIS hardness, or prove Fiat-Shamir security.
"""
from fractions import Fraction as F
from math import comb, factorial, isqrt


JL_MIN_SECURITY_BITS = 128
JL_SECURITY_MARGIN_BITS = 32
JL_BASE_FAILURE_BITS = 164
JL_BASE_ROWS = 1024


def jl_certificate():
    """Return rational upper bounds, using no floating-point decisions."""
    rows = JL_BASE_ROWS
    # Machin: pi=16 atan(1/5)-4 atan(1/239); alternating-series bounds.
    pi_lower = 16*(F(1,5)-F(1,3*5**3))-F(4,239)
    assert pi_lower > F(157,50)
    # Sum through degree six, and dominate the tail by a geometric series.
    e_upper_series = sum((F(1, factorial(k)) for k in range(7)), F(0)) + F(8, 7*factorial(7))
    assert e_upper_series < F(87, 32)
    assert sum((F(1, factorial(k)) for k in range(6)), F(0)) == F(163, 60)
    assert 120 < 11**2
    assert 144*F(239, 250)**2 > 131
    small_norm = F(87, 32)**60 * F(27, 32)**rows + 2048*F(60, 163)**131

    # Forty rows of magnitude >=q/144 exceed the allowed 120*(q/250)^2.
    assert F(40, 144**2) > F(120, 250**2)
    large_coordinate = F(sum(comb(rows, k) for k in range(40)), 2**rows)

    # Density bound, twice the Berry-Esseen discrepancy, and two tails.
    # Uses pi>157/50, general independent BE constant 0.56, and e>2.
    density_squared = F(144**2*120, 250**2*35) / F(157, 50)
    assert density_squared < F(6019, 10000)**2
    assert F(28, 25)**2 / 70 < F(1339, 10000)**2
    assert F(4, 2**36) < F(1, 10000)
    assert F(6019+1339+1, 10000) < F(736, 1000)
    spread = F(736, 1000)**rows
    target = F(1, 2**JL_BASE_FAILURE_BITS)
    assert all(bound < target for bound in (small_norm, large_coordinate, spread))
    return {
        "small_norm_upper": small_norm,
        "large_coordinate_upper": large_coordinate,
        "spread_upper": spread,
        "uniform_bound": target,
        "honest_rejection_upper": F(512, 512+40**2),
        "slack_squared": F(552, 120),
    }


def jl_security_profile(security_bits):
    """Integer JL family with failure <2^(-security_bits-32).

    Applies to a fixed centered vector, independent projection entries, and
    0<b<=q/K; see docs/jl-security-family.md for the all-parameter proof.
    J denotes projection rows and H the honest squared-norm multiplier.
    This profile does not parameterize the rest of a cryptographic protocol.
    """
    if type(security_bits) is not int or security_bits < JL_MIN_SECURITY_BITS:
        raise ValueError("security_bits must be an integer >=128")
    requested_bits = security_bits + JL_SECURITY_MARGIN_BITS
    k = (requested_bits + JL_BASE_FAILURE_BITS - 1) // JL_BASE_FAILURE_BITS
    n = 1 + isqrt(k - 1)
    base = jl_certificate()
    # These substitutions match the universal scaling proof, not a search.
    assert (n - 1)**2 < k <= n*n <= 2*k
    assert JL_BASE_FAILURE_BITS * (k - 1) < requested_bits <= JL_BASE_FAILURE_BITS * k
    return {
        "security_bits": security_bits,
        "security_margin_bits": JL_SECURITY_MARGIN_BITS,
        "scale_k": k,
        "ceil_sqrt_scale_n": n,
        "projection_rows_J": JL_BASE_ROWS * k,
        "bad_projection_squared_multiplier_alpha": 120 * k,
        "honest_projection_squared_multiplier_H": 552 * k,
        "small_norm_cutoff_A": 12 * n,
        "large_coordinate_cutoff_C": 72 * n,
        "modulus_cutoff_denominator_K": 250 * n*n,
        "failure_bound_exponent": JL_BASE_FAILURE_BITS * k,
        "requested_failure_bound_exponent": requested_bits,
        "uniform_failure_bound": base["uniform_bound"]**k,
        "honest_rejection_upper": F(8, 8 + 25*k),
        "honest_acceptance_lower": F(25*k, 8 + 25*k),
        "slack_squared": base["slack_squared"],
    }


def is_prime(q):
    """Deterministic trial division, intended for small example parameters."""
    if not isinstance(q, int) or q < 2:
        return False
    if q % 2 == 0:
        return q == 2
    d = 3
    while d*d <= q:
        if q % d == 0:
            return False
        d += 2
    return True


def challenge_cube(degree, radius=2):
    if degree < 2 or degree & (degree-1) or radius < 1:
        raise ValueError("degree must be a power of two >=2; radius must be positive")
    return {"cardinality": (2*radius+1)**degree,
            "operator_norm_bound": radius*degree,
            "l2_norm_squared_bound": radius*radius*degree,
            "difference_linf_bound": 2*radius}


def validate_ring(q, degree=64, radius=2):
    """Sufficient LS18 Cor. 1.2 conditions for invertible challenge differences."""
    challenge_cube(degree, radius)
    if not is_prime(q) or q % 8 != 5 or q <= 8*radius*radius:
        raise ValueError("need prime q=5 mod 8 and q>8*radius^2")
    return True


def aggregation_repetitions(q, security_bits):
    """Minimal integer m with q^m >= 2^security_bits, exactly."""
    if q < 2 or security_bits < 1:
        raise ValueError("q>=2 and security_bits>=1 required")
    count, power = 0, 1
    while power < 2**security_bits:
        power *= q
        count += 1
    return count


def statistical_budget(q, degree=64, aggregation_bits=160, radius=2):
    """Conditional one-attempt main-protocol budget, NOT full security.

    Requires the repaired algebraic/extraction theorem and commitment binding.
    Excludes optimized final-round, computational reduction, and FS losses.
    """
    validate_ring(q, degree, radius)
    m = aggregation_repetitions(q, aggregation_bits)
    n = challenge_cube(degree, radius)["cardinality"]
    return F(1, 2**164)+F(1, q**m)+F(1, q**(degree//2))+F(2, n)


def lifting_condition(beta_squared, dimension_count, degree, q):
    """Exact test sqrt(M*d/2)*beta+beta^2/2 < q/2."""
    beta_squared = F(beta_squared)
    if beta_squared < 0 or dimension_count < 0 or degree < 1 or q < 1:
        raise ValueError("nonnegative norms/counts and positive degree/q required")
    margin = F(q, 2)-beta_squared/2
    return margin > 0 and F(dimension_count*degree, 2)*beta_squared < margin**2


def repair_profile():
    """A mathematical profile, without a Module-SIS hardness certification."""
    q = 4294967197
    validate_ring(q)
    return {"rows": 1024, "q": q, "degree": 64,
            "bad_projection_squared_multiplier": 120,
            "honest_projection_squared_multiplier": 552,
            "modulus_cutoff_denominator": 250,
            "slack_squared": F(23, 5),
            "honest_rejection_upper": F(8, 33),
            **challenge_cube(64),
            "aggregation_repetitions": aggregation_repetitions(q, 160),
            "conditional_statistical_budget": statistical_budget(q),
            "status": "Mathematical profile only; no full protocol or security certification"}
