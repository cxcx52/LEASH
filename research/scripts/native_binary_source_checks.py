"""Offline integer/F2 checks for the native binary source/core interface.

No commitment, prover, extractor, random generator, or lattice solver is run.
"""

from fractions import Fraction as F
from itertools import product
from math import isqrt
import json
from pathlib import Path


def bar(poly):
    return (poly[0],)+tuple(-x for x in reversed(poly[1:]))


def mul(a, b):
    d = len(a)
    assert d == len(b)
    out = [0]*d
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i+j) % d] += x*y*(1 if i+j < d else -1)
    return tuple(out)


def dot(a, b):
    assert len(a) == len(b)
    return sum(x*y for x, y in zip(a, b))


def bit_lift_row(alpha, beta, gamma, eta, A, B, C, H, n):
    return tuple((sum(t*row[j] for t, row in zip(alpha, A))
                  + sum(t*row[j] for t, row in zip(beta, B))
                  + sum(t*row[j] for t, row in zip(gamma, C))
                  + sum(t*row[j] for t, row in zip(eta, H))) % 2
                 for j in range(n))


def main():
    identity_cases = 0
    bitness_cases = 0
    for d in (2, 4):
        jbar = bar((1,)*d)
        for u in product(range(-2, 3), repeat=d):
            assert bar(bar(u)) == u
            assert dot(u, u) == dot(bar(u), bar(u))
            assert mul(u, bar(u))[0] == dot(u, u)
            correct = mul(u, tuple(x-y for x, y in zip(bar(u), jbar)))[0]
            assert correct == sum(x*(x-1) for x in u)
            assert 0 <= correct <= 2*dot(u, u)
            identity_cases += 1
            if 2*dot(u, u) < 13:
                assert (correct % 13 == 0) == all(x in (0, 1) for x in u)
                bitness_cases += 1
        u = (0, 1)+(0,)*(d-2)
        scalar_one = (1,)+(0,)*(d-1)
        assert mul(u, tuple(x-y for x, y in zip(bar(u), scalar_one)))[0] == 1
        assert sum(x*(x-1) for x in u) == 0

    for a, b, c in product((0, 1), repeat=3):
        z = a+b-2*c
        assert 0 <= z*(z-1) <= 6
        assert (z*(z-1) == 0) == (a*b == c)

    # Exhaustive small source relation: H is optional in the theorem but present
    # here to verify that it enters delta before lifting without enlarging range.
    n, k, h = 4, 2, 1
    A = ((1, 1, 0, 0), (0, 0, 1, 1))
    B = ((1, 0, 1, 0), (0, 1, 0, 1))
    C = ((0, 1, 0, 0), (1, 0, 0, 1))
    H = ((1, 0, 1, 0),)
    row_checks = nonzero_residuals = 0
    for w in product((0, 1), repeat=n):
        Aw, Bw, Cw, Hw = (tuple(dot(row, w) % 2 for row in M)
                          for M in (A, B, C, H))
        for a, b in product(tuple(product((0, 1), repeat=k)), repeat=2):
            c = tuple(x*y for x, y in zip(a, b))
            residual = tuple((x-y) % 2 for x, y in zip(a, Aw))
            residual += tuple((x-y) % 2 for x, y in zip(b, Bw))
            residual += tuple((x-y) % 2 for x, y in zip(c, Cw))+Hw
            zeros = 0
            for challenges in product((0, 1), repeat=3*k+h):
                alpha, beta, gamma, eta = (challenges[:k], challenges[k:2*k],
                                           challenges[2*k:3*k], challenges[3*k:])
                delta = bit_lift_row(alpha, beta, gamma, eta, A, B, C, H, n)
                scalar = dot(alpha, a)+dot(beta, b)+dot(gamma, c)-dot(delta, w)
                assert -n <= scalar <= 3*k
                assert scalar % 2 == dot(challenges, residual) % 2
                zeros += scalar % 2 == 0
                row_checks += 1
            assert zeros == (2**(3*k+h-1) if any(residual) else 2**(3*k+h))
            nonzero_residuals += bool(any(residual))

    # A span less than q suffices for interval uniqueness, not centered parity.
    for lower, upper, q in ((-4, 6, 13), (-2, 3, 7), (-2, 6, 11)):
        assert upper-lower < q
        assert len({z % q for z in range(lower, upper+1)}) == upper-lower+1
    assert 4 % 2 == 0 and ((4+7//2) % 7-7//2) % 2 == 1

    # Explicit source-to-core block alignment and scalar communication.
    n = k = 2**25
    d, core_n, chunks, q, ell = 64, 37450, 14, 4294967197, 160
    D = n+3*k
    one_rings = n//d
    padded_rings = core_n*chunks
    assert one_rings == 524288 and padded_rings == 524300
    assert 8*padded_rings == 112*37450 == 4194400
    assert 8*(padded_rings-one_rings) == 96
    assert D//d == 2097152 and 2*D//d == 4194304
    beta_actual_sq = F(16, 3)*2*D
    assert 2*D == 2**28 and beta_actual_sq == F(4294967296, 3)
    assert beta_actual_sq < q and 6*k < q and n+3*k < q
    assert 2*max(n, 3*k) < q
    # The source collision radius sqrt(D), conservatively rounded upwards.
    collision_radius_ceiling = isqrt(D)+(isqrt(D)**2 < D)
    assert collision_radius_ceiling == 11586
    even_count = (3*k)//2-((-n+1)//2)+1
    assert even_count == 2**26+1
    scalar_bits = (even_count-1).bit_length()
    assert scalar_bits == 27 and ell*scalar_bits == 4320
    verifier_bits = ell*3*k
    assert verifier_bits == 16106127360
    assert F(verifier_bits, 8*2**30) == F(15, 8)
    assert F(3*k-1, 2**187) < F(1, 2**160)

    # A pure alignment identity in a small analogous padded layout.
    # Four ring entries per original block, two chunks of three after padding.
    dsmall, rings, width, count = 2, 4, 3, 2
    alignment_cases = 0
    for bits in product((0, 1), repeat=rings*dsmall):
        block = [tuple(bits[j:j+dsmall]) for j in range(0, len(bits), dsmall)]
        padded = block+[(0, 0)]*(width*count-rings)
        conj = [bar(u) for u in padded]
        total = sum(mul(u, v)[0] for u, v in zip(block, conj[:rings]))
        by_chunks = sum(mul(padded[width*j+t], conj[width*j+t])[0]
                        for j in range(count) for t in range(width))
        assert total == by_chunks == sum(bits)
        alignment_cases += 1

    result = {
        "scope": "Pure arithmetic source-interface checks; no cryptographic execution",
        "integer_identity_cases": identity_cases,
        "short_integer_bitness_cases": bitness_cases,
        "small_source_aggregation_rows": row_checks,
        "nonzero_residual_vectors": nonzero_residuals,
        "aligned_small_layout_cases": alignment_cases,
        "source_original_coefficient_count": D,
        "source_commitment_ring_columns": D//d,
        "source_collision_squared_radius": D,
        "source_collision_radius_ceiling": collision_radius_ceiling,
        "full_extracted_squared_cap": str(beta_actual_sq),
        "padded_witness_ring_length": 112*37450,
        "per_block_ring_padding": padded_rings-one_rings,
        "scalar_reply_width": scalar_bits,
        "source_scalar_reply_bytes": ell*scalar_bits//8,
        "source_verifier_challenge_bits": verifier_bits,
        "statistical_source_error": "2^-160, one aggregation stage",
        "computational_source_error": "sqrt(eta_src), complete two-suffix experiment",
        "all_assertions_passed": True,
    }
    path = Path(__file__).resolve().parents[1]/"work"/"native_binary_source_checks.json"
    path.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
