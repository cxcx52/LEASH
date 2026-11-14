"""Offline exact probability checks for LaBRADOR's published JL constants.

No protocol implementation, adversarial transcript, or target interaction.
All decisive inequalities use Python integers/Fraction; floats only display.
Run: python scripts/jl_exact_checks.py
"""

from fractions import Fraction as F
from math import comb, exp, isqrt, log2, pi, sqrt
import json


def binomial_upper_count(n, start):
    term = comb(n, start)
    total = term
    for k in range(start, n):
        term = term * (n - k) // (k + 1)
        total += term
    return total


def is_prime(n):
    if n < 2 or n % 2 == 0:
        return n == 2
    return all(n % d for d in range(3, isqrt(n) + 1, 2))


def describe(p):
    return {"probability": float(p), "log2_probability": log2(p)}


def main():
    # Existing two-coordinate counterexample, independently recomputed.
    old = F(sum(comb(256, k) for k in range(30)), 2**256)
    old += F(comb(256, 30), 2**256) * F(2**60 - comb(60, 30), 2**61)
    assert old > F(1, 2**128)

    # New stronger exact example in dimension 128.
    a, m, q = 2**21, 100, 4294967197
    assert is_prime(q)
    assert pow(q, 32, 128) == 1 and pow(q, 16, 128) != 1
    assert 125 * a < q and 2 * (a + m) < q  # hypotheses; no wrap
    assert a * a + m > a * a  # norm(w) > b=a
    assert 29 * a*a + 2*a*29*m + 256*m*m < 30*a*a
    assert 30 * a*a - 2*a + 256*m*m < 30*a*a
    new = F(sum(comb(256, k) for k in range(30)), 2**256)
    new += F(comb(256, 30), 2**256) * F(2**(60*m) - comb(60*m, 30*m), 2**(60*m+1))
    assert new > F(1, 2**127)
    limit = F(sum(comb(256, k) for k in range(30)), 2**256)
    limit += F(comb(256, 30), 2**257)

    # Exact all-ones example: ||w||=64, 9.5||w||=608.
    upper = F(2 * binomial_upper_count(8192, 4705), 2**8192)
    assert upper > F(1, 2**135)

    # Case 3 repair certificate. pi>3.14 and e>2 suffice for bounds.
    density_squared_bound = F(24, 25)**2 * F(6, 7) / F(157, 50)
    assert density_squared_bound < F(5016, 10000)**2
    assert F(28, 25)**2 / 70 < F(1339, 10000)**2
    assert F(4, 2**25) < F(1, 10000)
    assert F(5016 + 1339 + 1, 10000) < F(636, 1000)
    assert F(636, 1000)**256 < F(1, 2**167)
    case3_p = 24/25 * sqrt(6/(7*pi)) + 1.12/sqrt(70) + 4*exp(-25)

    out = {
        "old_lower_example": describe(old),
        "new_lower_example": {**describe(new), "ratio_to_2^-127": float(new*2**127), "a": a, "m": m, "q": q},
        "family_limit_lower_bound": describe(limit),
        "upper_tail_dimension_4096": {**describe(upper), "ratio_to_2^-141": float(upper*2**141)},
        "case3_repair": {"numeric_row_upper": case3_p, "numeric_log2_256rows": 256*log2(case3_p), "certified_bound": "< 2^-167"},
        "all_exact_assertions_passed": True,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
