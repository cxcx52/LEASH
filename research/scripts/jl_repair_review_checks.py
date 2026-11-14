"""Exact arithmetic certificates for the independent 1024-row JL review.

The probabilistic argument is in proofs/jl_repair_review.md. These checks
certify finite constants and boundary arithmetic, not a whole protocol.
Only Python standard library is required.
"""

from fractions import Fraction as F
from math import comb, factorial, log2, sqrt
import json


def main():
    e_lower = sum((F(1, factorial(k)) for k in range(6)), F(0))
    e_upper = sum((F(1, factorial(k)) for k in range(7)), F(0))
    e_upper += F(1, factorial(7)) * F(8, 7)
    assert e_lower == F(163, 60)
    assert e_upper == F(31967, 11760) < F(87, 32)
    assert 120 < 11**2
    assert 144 * F(239, 250)**2 > 131

    case1 = F(87, 32)**60 * F(27, 32)**1024
    case1 += 2048 * F(60, 163)**131
    assert case1 < F(1, 2**164)

    # Closed target event allows at most floor(39.81312)=39 countable rows.
    case2_count_limit = F(120 * 144**2, 250**2)
    assert 39 < case2_count_limit < 40
    assert F(40, 144**2) > F(120, 250**2)
    case2 = F(sum(comb(1024, k) for k in range(40)), 2**1024)
    assert case2 < F(1, 2**788)

    # Case 3 constants: pi>3.14 and e>2 suffice.
    # Machin identity + alternating arctangent series certify the pi bound.
    pi_lower = 16 * (F(1, 5) - F(1, 3 * 5**3)) - F(4, 239)
    assert pi_lower == F(281476, 89625) > F(157, 50)
    density_squared = F(144**2 * 120, 250**2 * 35) / F(157, 50)
    assert density_squared < F(6019, 10000)**2
    assert F(28, 25)**2 / 70 < F(1339, 10000)**2
    assert F(4, 2**36) < F(1, 10000)
    assert F(6019 + 1339 + 1, 10000) < F(736, 1000)
    case3 = F(736, 1000)**1024
    assert case3 < F(1, 2**452)
    assert max(case1, case2, case3) < F(1, 2**164)

    # Public completeness parameters and exact slack squared.
    assert F(512, 512 + (552 - 512)**2) == F(8, 33)
    assert 1 - F(8, 33) == F(25, 33)
    assert F(552, 120) == F(23, 5)
    assert 1 - F(512, 512 + (535 - 512)**2) == F(529, 1041)
    assert 1 - F(512, 512 + (1024 - 512)**2) == F(512, 513)

    print(json.dumps({
        "all_exact_assertions_passed": True,
        "closed_event_uniform_certificate": "< 2^-164",
        "case1_rational_bound_log2": log2(case1),
        "case2_exact_binomial_bound_log2": log2(case2),
        "case2_count_limit": str(case2_count_limit),
        "case3_rational_bound_log2": log2(case3),
        "honest_squared_threshold": 552,
        "honest_acceptance_lower_bound": "25/33",
        "soundness_slack_squared": "23/5",
        "soundness_slack_decimal_display": sqrt(23 / 5),
    }, indent=2))


if __name__ == "__main__":
    main()
