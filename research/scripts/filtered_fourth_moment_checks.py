"""Pure exact-moment checks for filtered challenges and stacked ring vectors.

Finite arithmetic checks support the proof in proofs/filtered_fourth_moment.md.
They are not a cryptographic implementation or a substitute for the proof.
"""

from fractions import Fraction as F
from itertools import product
import json

from certified_filtered_challenges_checks import (
    certified_op_below, negacyclic_matrix, tail_certificate,
)


def transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def matmul(left, right):
    columns = transpose(right)
    return [[sum(x*y for x, y in zip(row, column)) for column in columns]
            for row in left]


def frobenius_squared(matrix):
    return sum(x*x for row in matrix for x in row)


def trace(matrix):
    return sum(matrix[j][j] for j in range(len(matrix)))


def stacked_multiplication(blocks):
    return [row for block in blocks for row in negacyclic_matrix(block)]


def apply(matrix, vector):
    return tuple(sum(x*y for x, y in zip(row, vector)) for row in matrix)


def energy(vector):
    return sum(x*x for x in vector)


def vector_moments(vectors):
    count = len(vectors)
    mean = tuple(F(sum(v[j] for v in vectors), count) for j in range(len(vectors[0])))
    second = F(sum(energy(v) for v in vectors), count)
    fourth = F(sum(energy(v)**2 for v in vectors), count)
    return mean, second, fourth


def structural_checks(blocks):
    degree = len(blocks[0])
    block_count = len(blocks)
    matrix = stacked_multiplication(blocks)
    j = negacyclic_matrix(tuple(int(k == degree//2) for k in range(degree)))
    output_j = [[j[row % degree][column % degree]
                 if row//degree == column//degree else 0
                 for column in range(block_count*degree)]
                for row in range(block_count*degree)]
    assert matmul(matrix, j) == matmul(output_j, matrix)
    assert matmul(j, j) == [[-int(row == column) for column in range(degree)]
                            for row in range(degree)]
    assert transpose(j) == [[-x for x in row] for row in j]
    gram = matmul(transpose(matrix), matrix)
    output_gram = matmul(matrix, transpose(matrix))
    assert matmul(gram, j) == matmul(j, gram)
    assert matmul(output_gram, output_j) == matmul(output_j, output_gram)
    t = sum(energy(block) for block in blocks)
    assert all(gram[k][k] == t for k in range(degree))
    assert trace(gram) == degree*t
    assert frobenius_squared(gram) <= F(trace(gram)**2, 2)
    return matrix, gram, t


def check_instance(degree, threshold, witnesses):
    cube = tuple(product(range(-2, 3), repeat=degree))
    selected = tuple(c for c in cube if certified_op_below(c, threshold))
    p = F(len(selected), len(cube))
    v = F(sum(c[0]**2 for c in selected), len(selected))
    assert all(sum(c[j] for c in selected) == 0 for j in range(degree))
    assert all(F(sum(c[i]*c[j] for c in selected), len(selected))
               == (v if i == j else 0)
               for i in range(degree) for j in range(degree))
    assert v <= 2/p
    assert (v-2)**2 <= F(14, 5*degree)*(1-p)/p
    matrices, energies, filtered_vectors, second_moments, fourth_moments = [], [], [], [], []
    h = 8 - F(26, 5*degree)
    g = h - 4
    for blocks in witnesses:
        matrix, gram, t = structural_checks(blocks)
        raw = tuple(apply(matrix, c) for c in cube)
        chosen = tuple(apply(matrix, c) for c in selected)
        raw_mean, raw_second, raw_fourth = vector_moments(raw)
        mean, second, fourth = vector_moments(chosen)
        exact_raw_formula = (4*trace(gram)**2 + 8*frobenius_squared(gram)
                             - F(26, 5)*sum(gram[j][j]**2 for j in range(degree)))
        assert all(value == 0 for value in raw_mean + mean)
        assert raw_second == 2*degree*t
        assert raw_fourth == exact_raw_formula
        assert raw_fourth <= degree**2*h*t*t
        assert raw_fourth - raw_second**2 <= degree**2*g*t*t
        if degree == 2:
            assert raw_fourth == degree**2*h*t*t
        assert second == v*degree*t
        assert fourth <= raw_fourth/p <= degree**2*h*t*t/p
        assert fourth - second**2 <= degree**2*t*t*(g/p - (v-2)**2)
        matrices.append(matrix)
        energies.append(t)
        filtered_vectors.append(chosen)
        second_moments.append(second)
        fourth_moments.append(fourth)

    fourth_expansion = sum(fourth_moments)
    cross_checks = 0
    for i in range(len(witnesses)):
        for j in range(i + 1, len(witnesses)):
            cross_gram = matmul(transpose(matrices[i]), matrices[j])
            inner_squared = v*v*frobenius_squared(cross_gram)
            observed_inner_squared = F(sum(sum(x*y for x, y in zip(left, right))**2
                                           for left in filtered_vectors[i]
                                           for right in filtered_vectors[j]),
                                       len(selected)**2)
            assert inner_squared == observed_inner_squared
            assert inner_squared <= second_moments[i]*second_moments[j]/2
            fourth_expansion += 2*second_moments[i]*second_moments[j] + 4*inner_squared
            cross_checks += 1

    output_dimension = len(filtered_vectors[0][0])
    combined_second = combined_fourth = 0
    combined_cases = 0
    for draws in product(*filtered_vectors):
        squared = sum(sum(draw[j] for draw in draws)**2 for j in range(output_dimension))
        combined_second += squared
        combined_fourth += squared*squared
        combined_cases += 1
    combined_second = F(combined_second, combined_cases)
    combined_fourth = F(combined_fourth, combined_cases)
    assert combined_second == sum(second_moments)
    assert combined_fourth == fourth_expansion
    total = sum(energies)
    squares = sum(t*t for t in energies)
    variance = combined_fourth - combined_second**2
    detailed_upper = degree**2*(v*v*total*total + (h/p - 2*v*v)*squares)
    envelope_upper = degree**2*total*total*max(h/p - v*v, v*v)
    assert 0 <= variance <= detailed_upper <= envelope_upper
    centered_detailed = degree**2*(v*v*total*total
                                   + (g/p - (v-2)**2 - v*v)*squares)
    centered_envelope = degree**2*total*total*max(g/p - (v-2)**2, v*v)
    assert variance <= centered_detailed <= centered_envelope
    assert centered_detailed <= detailed_upper
    assert combined_fourth <= 12*degree**2*total*total/(p*p)
    return {
        "degree": degree, "threshold": threshold,
        "vector_blocks": len(witnesses[0]), "independent_challenges": len(witnesses),
        "selected_count": len(selected), "p": str(p), "sigma_squared": str(v),
        "combined_exact_enumeration_cases": combined_cases,
        "cross_covariance_checks": cross_checks,
        "exact_variance": str(variance),
        "variance_upper_with_known_p_v_and_energies": str(detailed_upper),
        "centered_variance_upper_with_known_p_v_and_energies": str(centered_detailed),
    }


def cap_certificate(coefficient, degree, acceptance_lower, failure_upper):
    """Rational checks sufficient for both terms of the no-sqrt cap formula."""
    h = 8 - F(26, 5*degree)
    k = (1 - failure_upper)/failure_upper
    margin = coefficient*acceptance_lower/2 - 1
    return (margin >= 0 and margin*margin >= k
            and coefficient*coefficient >= h/(acceptance_lower*failure_upper))


def checks():
    d2_a = ((1, 2), (-1, 1))
    d2_b = ((0, 1), (2, -1))
    d2_c = ((-1, 2), (1, 0))
    d4_a = ((1, -2, 0, 1), (0, 1, 1, 0))
    d4_b = ((2, 0, -1, 1), (-1, 0, 1, 2))
    instances = [check_instance(2, 2, (d2_a, d2_b, d2_c)),
                 check_instance(2, 3, (d2_a, d2_b)),
                 check_instance(4, 4, (d4_a, d4_b))]
    scalar_cases = 0
    for degree in (2, 4, 64):
        h = 8 - F(26, 5*degree)
        for acceptance in (F(1, 2), F(9, 16), F(3, 4)):
            for failure in (F(1, 2), F(1, 4), F(1, 16), F(1, 64)):
                cap = 1
                while not cap_certificate(F(cap), degree, acceptance, failure):
                    cap += 1
                k = (1-failure)/failure
                for p_index in range(9):
                    p = acceptance + (1-acceptance)*F(p_index, 8)
                    for v_index in range(9):
                        v = F(v_index, 8)*2/p
                        upper = max(h/p - v*v, v*v)
                        assert cap > v
                        assert (cap-v)**2 >= k*upper
                        scalar_cases += 1
    exact_cap = F(52, 3)
    acceptance, failure = F(9, 16), F(1, 16)
    assert cap_certificate(exact_cap, 64, acceptance, failure)
    assert (exact_cap*acceptance/2-1)**2 == F(961, 64) > 15
    # The first exact radical term dominates for d64,a9/16,f1/16:
    # after squaring, dominance is 4+(1/2)*sqrt(15)>a*h.
    # The elementary lower bound sqrt(15)>3 already suffices here.
    h64 = 8 - F(26, 5*64)
    assert F(4, 1)*(1+2*F(3, 16)) > acceptance*h64
    improved_acceptance, improved_failure = F(901, 1024), F(1, 16)
    assert tail_certificate(64, 34, 123, 1024)
    assert cap_certificate(F(12), 64, improved_acceptance, improved_failure)
    assert 144 - h64/(improved_acceptance*improved_failure) == F(16, 4505)
    centered_cap = F(21, 2)
    g64 = h64 - 4
    rho_squared = F(14, 5*64)*(1-improved_acceptance)/improved_acceptance
    assert rho_squared == F(861, 144160) < F(1, 144)
    assert (centered_cap-2)**2 - g64/(improved_acceptance*improved_failure) == F(17849, 18020)
    assert F(31, 8)**2 > 15
    assert (2+F(1, 12))*(1+F(31, 8)) == F(325, 32) < centered_cap
    centered_scalar_cases = 0
    for p_index in range(9):
        p = improved_acceptance + (1-improved_acceptance)*F(p_index, 8)
        for shift in range(-16, 17):
            v = 2 + F(shift, 64)
            if (v-2)**2 <= F(14, 5*64)*(1-p)/p:
                upper = max(g64/p-(v-2)**2, v*v)
                assert centered_cap > v
                assert (centered_cap-v)**2 >= 15*upper
                centered_scalar_cases += 1
    return {"scope": "Exact finite moment checks, not a security estimate",
            "instances": instances,
            "rational_parameter_grid_cases": scalar_cases,
            "d64_certified_gamma_squared_coefficient": str(exact_cap),
            "filter_acceptance_lower": str(acceptance),
            "fold_rejection_upper": str(failure),
            "T34_filter_acceptance_lower": str(improved_acceptance),
            "T34_paired_cap_coefficient": "12",
            "T34_centered_cap_coefficient": str(centered_cap),
            "centered_parameter_grid_cases": centered_scalar_cases,
            "all_checks_passed": True}


if __name__ == "__main__":
    print(json.dumps(checks(), indent=2))
