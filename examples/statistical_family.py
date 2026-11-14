"""Exact statistical accounting, excluding computational reduction losses.

The norm example checks the JL modulus condition only. No affine witness
dimension or affine norm is supplied, so affine lifting is not certified.
"""

import json
from fractions import Fraction as F

from labrador_repair.bounds import (
    aggregation_repetitions,
    jl_security_profile,
    validate_ring,
)


def statistical_example(security_bits, multiplicity, q, beta_squared=F(1)):
    """Check one illustrative profile with exact arithmetic."""
    jl = jl_security_profile(security_bits)
    if type(multiplicity) is not int or multiplicity < 1:
        raise ValueError("multiplicity must be a positive integer")
    beta_squared = F(beta_squared)
    if beta_squared <= 0:
        raise ValueError("this JL soundness example requires beta_squared>0")

    target_bits = security_bits + 32
    h = (multiplicity + 1).bit_length()  # ceil(log2(r+2))
    degree = 1 << (target_bits + h - 1).bit_length()
    validate_ring(q, degree=degree, radius=2)
    repetitions = aggregation_repetitions(q, target_bits)
    cutoff = jl["modulus_cutoff_denominator_K"]
    if cutoff*cutoff*jl["slack_squared"]*beta_squared > q*q:
        raise ValueError("the example does not satisfy the JL modulus condition")

    epsilon = F(1, 2**target_bits)
    terms = {
        "jl_certificate": jl["uniform_failure_bound"],
        "scalar_aggregation": F(1, q**repetitions),
        "crt_aggregation": F(1, q**(degree // 2)),
        "challenge": F(multiplicity + 2, 5**degree),
    }
    assert multiplicity + 2 <= 2**h
    assert target_bits + h <= degree < 2*(target_bits + h)
    assert q**(repetitions-1) < 2**target_bits <= q**repetitions
    assert all(term <= epsilon for term in terms.values())
    ordinary_sum = sum(terms.values(), F(0))
    # The JL theorem is strict below its certificate. The other terms also
    # leave strict room in the rational sums checked for these examples.
    assert ordinary_sum < 4*epsilon

    affine_repetitions = target_bits
    affine_statistical_term = F(2, 3**affine_repetitions)  # smallest prime p>=3
    assert affine_statistical_term <= 2*epsilon
    assert ordinary_sum + affine_statistical_term < 6*epsilon
    assert 6*epsilon < F(1, 2**(security_bits+29))

    return {
        "security_bits": security_bits,
        "multiplicity_r": multiplicity,
        "q": q,
        "ring_degree_d": degree,
        "scalar_aggregation_m": repetitions,
        "affine_repetitions_ell": affine_repetitions,
        "projection_rows_J": jl["projection_rows_J"],
        "jl_modulus_cutoff_K": cutoff,
        "ordinary_statistical_bound": f"<2^-{security_bits+30}",
        "with_affine_statistical_bound": f"<2^-{security_bits+29}",
        "source_modulus_bit_length": degree + 1,
        "exact_arithmetic_checks_passed": True,
        "jl_beta_squared_example": str(beta_squared),
        "jl_modulus_condition_checked": True,
        "affine_statistical_term_checked_using_p_at_least_3": True,
        "affine_lifting_condition_checked": False,
    }


if __name__ == "__main__":
    profiles = [statistical_example(bits, bits*bits, 4294967197)
                for bits in (128, 256, 512)]
    print(json.dumps({
        "scope": "Statistical arithmetic only; computational reduction losses are excluded",
        "affine_lifting": "Not checked: no affine witness dimension or affine norm bound supplied",
        "profiles": profiles,
    }, indent=2))
