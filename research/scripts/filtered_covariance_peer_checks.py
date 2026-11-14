"""Independent finite checks for the filtered-cube covariance symmetry proof."""
from fractions import Fraction
from itertools import product
from math import gcd
import json

from certified_filtered_challenges_checks import certified_op_below


def substitute(coefficients, exponent):
    d = len(coefficients)
    out = [0] * d
    for j, value in enumerate(coefficients):
        degree = j * exponent % (2*d)
        out[degree % d] = value * (1 if degree < d else -1)
    return tuple(out)


def shift(coefficients, power):
    d = len(coefficients)
    out = [0] * d
    for j, value in enumerate(coefficients):
        degree = (j + power) % (2*d)
        out[degree % d] = value * (1 if degree < d else -1)
    return tuple(out)


def main():
    involution_checks = 0
    for d in (2, 4, 8, 16, 32, 64, 128, 256):
        for delta in range(1, d):
            two_part = delta & -delta
            exponent = 1 + d // two_part
            assert gcd(exponent, 2*d) == 1
            assert exponent * delta % (2*d) == delta + d
            assert substitute((1,) + (0,)*(d-1), exponent) == (1,) + (0,)*(d-1)
            basis = tuple(int(j == delta) for j in range(d))
            assert substitute(basis, exponent) == tuple(-value for value in basis)
            involution_checks += 1

    results = []
    for d, threshold in ((2, 2), (2, 3), (4, 3), (4, 4), (4, 5)):
        cube = tuple(product(range(-2, 3), repeat=d))
        selected = {c for c in cube if certified_op_below(c, threshold)}
        assert selected
        for c in selected:
            assert tuple(-x for x in c) in selected
            assert all(shift(c, j) in selected for j in range(d))
            assert all(substitute(c, a) in selected for a in range(1, 2*d, 2))
        assert all(sum(c[j] for c in selected) == 0 for j in range(d))
        covariance = [[Fraction(sum(c[i]*c[j] for c in selected), len(selected))
                       for j in range(d)] for i in range(d)]
        variance = covariance[0][0]
        assert all(covariance[i][j] == (variance if i == j else 0)
                   for i in range(d) for j in range(d))
        assert variance <= Fraction(2 * 5**d, len(selected))
        results.append({"d": d, "strict_threshold": threshold,
                        "cardinality": len(selected), "variance": str(variance)})
    print(json.dumps({"basis_flip_checks": involution_checks,
                      "exact_filtered_covariance_instances": results}, indent=2))


if __name__ == "__main__":
    main()
