"""Finite exact checks for the architecture propositions.

These are arithmetic/ring-identity checks, not a protocol implementation.
"""
from fractions import Fraction as F
from itertools import product
from math import isqrt
import json


def next_lower(w, r, kappa):
    return F(2*w, r) + 2*r*r + 2*(kappa+1)*r


def negacyclic_mul(a, b):
    d = len(a)
    out = [0]*d
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i+j)%d] += x*y*(1 if i+j<d else -1)
    return tuple(out)


def smallest_prime(n):
    return next((p for p in range(2,isqrt(n)+1) if n%p==0),n)


def main():
    floors = {}
    floor_checks = 0
    for kappa in range(1,129):
        floor = min(18*kappa+72,16*kappa+80)
        values = [F(2*r*r*(r+kappa+1),r-2) for r in range(3,257)]
        assert min(values) == floor
        for r in range(1,257):
            assert next_lower(floor,r,kappa) >= floor
            assert next_lower(floor-1,r,kappa) >= floor-1
            assert next_lower(floor+1,r,kappa) >= floor
            floor_checks += 1
        floors[kappa] = floor
    assert floors[1] == 90
    assert floors[4] == 144
    amgm_checks = 0
    for w in range(1,257):
        for r in range(1,65):
            base = F(2*w,r)+2*r*r
            assert base**3 >= 54*w*w
            amgm_checks += 1
    parity_checks = 0
    for d in (2,4):
        polys = tuple(product((-1,0,1),repeat=d))
        for a in polys:
            for b in polys:
                assert sum(negacyclic_mul(a,b))%2 == (sum(a)%2)*(sum(b)%2)
                parity_checks += 1
    # The parity homomorphism lives on the integer ring, not directly on R_q.
    assert 13%2 != 0%2 and 13%13 == 0%13
    tight_sources = {}
    for n in (4,8,15,17,65,257):
        p = smallest_prime(n)
        e = n//p
        zeros = sum((u*e)%n == 0 for u in range(n))
        assert F(zeros,n) == F(1,p)
        tight_sources[n] = str(F(zeros,n))
    print(json.dumps({
        'all_assertions_passed':True,
        'discrete_floor_checks':floor_checks,
        'floor_kappa_1':floors[1],
        'floor_kappa_4':floors[4],
        'continuous_cubic_checks':amgm_checks,
        'parity_homomorphism_pairs':parity_checks,
        'tight_source_batching_probabilities':tight_sources,
        'scope':'finite certificates supplement the universal proofs'
    },indent=2))


if __name__ == '__main__':
    main()
