"""Exact affine-R1CS algebra behind the repaired reduction.

This module checks arithmetic and lifting. It does not implement commitments,
an interactive prover, Fiat-Shamir, or a cryptographic security reduction.
"""
from .ring import encode, negacyclic_multiply


def matvec(matrix, vector, modulus):
    if any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix/vector shape mismatch")
    return tuple(sum(a*b for a,b in zip(row, vector)) % modulus for row in matrix)


def source_relation(A, B, C, H, w, modulus):
    if not w or w[0] % modulus != 1:
        return False
    a, b, c = (matvec(matrix, w, modulus) for matrix in (A, B, C))
    if not (len(a) == len(b) == len(c)):
        raise ValueError("R1CS row count mismatch")
    return (all((x*y-z) % modulus == 0 for x,y,z in zip(a,b,c))
            and all(v == 0 for v in matvec(H, w, modulus)))


def linear_coefficients(A, B, C, H, phi, alpha, beta, gamma, delta, eta, row, modulus):
    """Collect coefficients in the semantic ring BEFORE encoding.

    Ordering is (a,b,c,w,d_1,...,d_l); each delta[j] tests phi[j]*a-d_j.
    """
    if modulus < 2 or not A or not A[0]:
        raise ValueError("need modulus>=2 and nonempty R1CS dimensions")
    k, n, ell = len(A), len(A[0]), len(phi)
    if (len(B) != k or len(C) != k or len(alpha) != k or len(beta) != k
        or len(gamma) != k or len(delta) != ell or len(eta) != len(H)
        or not 0 <= row < ell or any(len(x) != k for x in list(phi)+list(delta))
        or any(len(x) != n for x in list(A)+list(B)+list(C)+list(H))):
        raise ValueError("aggregation shape mismatch")
    ca = [-alpha[t]+sum(delta[j][t]*phi[j][t] for j in range(ell)) for t in range(k)]
    cb = [-v for v in beta]
    cc = [-gamma[t]-phi[row][t] for t in range(k)]
    cw = [sum(A[t][u]*alpha[t]+B[t][u]*beta[t]+C[t][u]*gamma[t] for t in range(k))
          +sum(H[t][u]*eta[t] for t in range(len(H))) for u in range(n)]
    cd = [-delta[j][t] for j in range(ell) for t in range(k)]
    return tuple(v % modulus for v in ca+cb+cc+cw+cd)


def encoded_residual(coefficients, witness, degree, k, n, ell, row):
    """Compute the integer-ring F_i, before reduction modulo q."""
    if (min(k,n,ell) < 1 or not 0 <= row < ell
        or len(witness) != n+(3+ell)*k or len(coefficients) != len(witness)
        or any(len(p) != degree for p in witness)):
        raise ValueError("witness shape mismatch")
    result = [0]*degree
    def accumulate(product):
        for j, value in enumerate(product):
            result[j] += value
    for coefficient, value in zip(coefficients, witness):
        accumulate(negacyclic_multiply(encode(coefficient, degree), value))
    for j in range(k):
        accumulate(negacyclic_multiply(witness[k+j], witness[3*k+n+row*k+j]))
    return tuple(result)
