"""Integer security-family profiles and exact base certificates.

The all-lambda proof is in proofs/jl_security_family.md. Finite example
profiles are illustrations, not the justification of the universal theorem.
This draft does not modify the public package.
"""

from fractions import Fraction as F
from math import comb, factorial, isqrt, log2
import json
import sys


def family_constants_certificate():
    """Certify the three fixed rational bases used for every integer scale."""
    assert sum((F(1, factorial(j)) for j in range(6)), F(0)) == F(163, 60)
    e_upper = sum((F(1, factorial(j)) for j in range(7)), F(0))
    e_upper += F(8, 7 * factorial(7))
    assert e_upper < F(87, 32)
    assert 144 * F(239, 250)**2 > 131
    assert 120 < 11**2
    a = F(87, 32)**60 * F(27, 32)**1024
    c = 2048 * F(60, 163)**131
    u = a + c
    v = F(sum(comb(1024, j) for j in range(40)), 2**1024)

    pi_lower = 16 * (F(1, 5) - F(1, 3 * 5**3)) - F(4, 239)
    assert pi_lower > F(157, 50)
    density_squared = F(144**2 * 120, 250**2 * 35) / F(157, 50)
    assert density_squared < F(6019, 10000)**2
    assert F(28, 25)**2 / 70 < F(1339, 10000)**2
    assert F(4, 2**36) < F(1, 10000)
    assert F(6019 + 1339 + 1, 10000) < F(736, 1000)
    w = F(736, 1000)**1024
    assert u < F(1, 2**164)
    assert v < F(1, 2**788)
    assert w < F(1, 2**452)
    return {"case1_base": u, "case2_base": v, "case3_base": w}


def security_profile(security_bits):
    """Integer parameters for every integer lambda>=128.

    The projection failure is strictly below 2^(-164*k), which is at most
    2^(-lambda-32), under the hypotheses stated in the mathematical proof.
    """
    if type(security_bits) is not int or security_bits < 128:
        raise ValueError("security_bits must be an integer >=128")
    k = (security_bits + 32 + 163) // 164
    n = 1 + isqrt(k - 1)
    return {
        "security_bits": security_bits,
        "scale_k": k,
        "ceil_sqrt_k": n,
        "rows_m": 1024 * k,
        "bad_squared_multiplier_alpha": 120 * k,
        "honest_squared_multiplier_T": 552 * k,
        "case1_denominator_A": 12 * n,
        "case2_denominator_C": 72 * n,
        "modulus_cutoff_denominator_K": 250 * n * n,
        "certified_failure_exponent": 164 * k,
        "requested_failure_exponent": security_bits + 32,
        "honest_rejection_upper": F(8, 8 + 25 * k),
        "honest_acceptance_lower": F(25 * k, 8 + 25 * k),
        "slack_squared": F(23, 5),
    }


def check_profile_structure(profile):
    """Check exact substitution identities for one profile.

    The document proves the scaling inequalities for all k; this routine is
    a check on the parameter-generation implementation.
    """
    k = profile["scale_k"]
    n = profile["ceil_sqrt_k"]
    m = profile["rows_m"]
    alpha = profile["bad_squared_multiplier_alpha"]
    threshold = profile["honest_squared_multiplier_T"]
    a = profile["case1_denominator_A"]
    c = profile["case2_denominator_C"]
    cutoff = profile["modulus_cutoff_denominator_K"]
    assert (n - 1)**2 < k <= n*n <= 2*k
    assert 164*k >= profile["security_bits"] + 32
    assert c == 6*a and a >= 12
    assert F(threshold, alpha) == F(23, 5)
    assert F(4*alpha*c*c, cutoff*cutoff) == F(124416, 3125) * F(k, n*n)
    assert F(4*alpha*c*c, cutoff*cutoff) < 40
    assert F(k, n*n) <= 1  # squared density ratio against the base case
    assert F(alpha, cutoff*cutoff) <= F(120, 250**2) / k
    assert a*a >= 144*k
    assert F(m, 2) / (F(m, 2) + (threshold - F(m, 2))**2) == F(8, 8+25*k)
    assert profile["honest_acceptance_lower"] >= F(25, 33)
    assert 250*k <= cutoff <= 500*k
    return True


def main(args):
    bases = family_constants_certificate()
    values = [int(value) for value in args] if args else [128, 256, 512, 1024]
    profiles = []
    for value in values:
        profile = security_profile(value)
        check_profile_structure(profile)
        profiles.append({key: str(val) if isinstance(val, F) else val
                         for key, val in profile.items()})
    print(json.dumps({
        "fixed_rational_certificates_passed": True,
        "base_log2_values_for_display_only": {key: log2(value) for key, value in bases.items()},
        "universal_proof": "proofs/jl_security_family.md; no lambda enumeration is used in the proof",
        "profiles": profiles,
    }, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
