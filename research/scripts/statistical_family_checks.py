"""Exact arithmetic examples for proofs/statistical_family.md.

No prover, prime-search algorithm, or Module-SIS security estimator is used.
Trial-division primality checking is for the small example modulus only.
"""

from fractions import Fraction as F
from math import isqrt
import json

from jl_family_checks import family_constants_certificate, security_profile


def is_prime_example(q):
    if q < 2 or q % 2 == 0:
        return q == 2
    return all(q % divisor for divisor in range(3, isqrt(q) + 1, 2))


def statistical_profile(security_bits, multiplicity, q):
    jl = security_profile(security_bits)
    if type(multiplicity) is not int or multiplicity < 1:
        raise ValueError("multiplicity must be a positive integer")
    if type(q) is not int or q <= 32 or q % 8 != 5 or not is_prime_example(q):
        raise ValueError("q must be a prime >32 with q=5 mod 8")
    target_bits = security_bits + 32
    h = (multiplicity + 1).bit_length()  # ceil(log2(r+2))
    d = 1 << (target_bits + h - 1).bit_length()
    m, power = 0, 1
    while power < 2**target_bits:
        m += 1
        power *= q
    epsilon = F(1, 2**target_bits)
    terms = {
        "jl": F(1, 2**jl["certified_failure_exponent"]),
        "scalar_aggregation": F(1, q**m),
        "crt_aggregation": F(1, q**(d // 2)),
        "challenge": F(multiplicity + 2, 5**d),
    }
    assert multiplicity + 2 <= 2**h
    assert target_bits + h <= d < 2*(target_bits + h)
    assert q**(m-1) < 2**target_bits <= q**m
    assert all(term <= epsilon for term in terms.values())
    # The JL theorem is strict below its certificate. Here the three other
    # terms also leave enough strict room for the displayed rational sum.
    ordinary = sum(terms.values(), F(0))
    assert ordinary < 4*epsilon
    ell = target_bits
    affine = F(2, 3**ell)  # p>=3; no source-modulus factorization needed
    assert affine <= 2*epsilon
    assert ordinary + affine < 6*epsilon < F(1, 2**(security_bits+29))
    return {
        "security_bits": security_bits,
        "multiplicity_r": multiplicity,
        "q": q,
        "degree_d": d,
        "aggregation_m": m,
        "affine_ell": ell,
        "projection_rows_J": jl["rows_m"],
        "jl_modulus_denominator_K": jl["modulus_cutoff_denominator_K"],
        "ordinary_budget_exponent": security_bits + 30,
        "combined_budget_exponent": security_bits + 29,
        "source_modulus_bit_length": d + 1,
        "exact_arithmetic_checks_passed": True,
    }


def main():
    family_constants_certificate()
    profiles = [statistical_profile(bits, bits*bits, 4294967197)
                for bits in (128, 256, 512)]
    # Illustrate the JL modulus condition at beta^2=1, separately from the
    # arithmetic error budget. Affine lifting requires its own M and norm.
    for profile in profiles:
        cutoff = profile["jl_modulus_denominator_K"]
        assert cutoff*cutoff*F(23, 5) <= profile["q"]**2
    print(json.dumps({
        "profiles": profiles,
        "jl_modulus_condition_checked_at_beta_squared": 1,
        "affine_lifting_condition": "requires M and beta_aff; not certified by these examples",
        "universal_proof": "proofs/statistical_family.md",
    }, indent=2))


if __name__ == "__main__":
    main()
