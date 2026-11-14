"""Exact, offline algebra checks for LaBRADOR section 6 (34-page local PDF).
This verifies honest arithmetic and lifting counterexamples, not protocol attacks.
Run: python scripts/r1cs_checks.py
"""
from fractions import Fraction
from math import isqrt, sqrt
import json

D = 4
N = 2**D + 1
Q = 13


def naf(value, d=D):
    modulus = 2**d + 1
    value %= modulus
    z = value if value <= modulus // 2 else value - modulus
    digits = [0] * d
    i = 0
    while z:
        digit = 0 if z % 2 == 0 else 2 - z % 4
        assert i < d
        digits[i] = digit
        z = (z - digit) // 2
        i += 1
    return tuple(digits)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def mul(a, b):
    assert len(a) == len(b)
    d = len(a)
    c = [0] * d
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[(i+j) % d] += x*y*(1 if i+j < d else -1)
    return tuple(c)


def evaluate(a):
    return sum(x*2**i for i, x in enumerate(a))


def norm_sq(a):
    return sum(x*x for x in a)


def centered(a, q):
    return tuple((x + q//2) % q - q//2 for x in a)


def is_prime(q):
    return q >= 2 and all(q % p for p in range(2, isqrt(q)+1))


def main():
    encoding = {v: naf(v) for v in range(N)}
    for v, poly in encoding.items():
        assert evaluate(poly) % N == v
        assert all(x in (-1, 0, 1) for x in poly)
        assert norm_sq(poly) <= D//2
        assert all(poly[i] * poly[i+1] == 0 for i in range(D-1))

    # X^4+1=(X^2+5)(X^2+8) mod 13, both factors irreducible.
    assert is_prime(Q)
    assert (5+8) % Q == 0 and (5*8) % Q == 1
    squares = {x*x % Q for x in range(Q)}
    assert (-5) % Q not in squares and (-8) % Q not in squares

    A, B, C, w = 15, 11, 14, 4
    a, b, c = A*w % N, B*w % N, C*w % N
    phi, alpha, beta_challenge, gamma, delta = 3, 12, 8, 2, 7
    d1 = phi*a % N
    assert (a,b,c,d1) == (9,10,5,10)
    assert a*b % N == c
    assert phi*a % N == d1
    assert (d1*b - phi*c) % N == 0

    # Expand f before replacing its five linear coefficients by Enc.
    coeff = ((-alpha + delta*phi) % N,
             -beta_challenge % N,
             (-gamma-phi) % N,
             (alpha*A + beta_challenge*B + gamma*C) % N,
             -delta % N)
    assert coeff == (9, 9, 12, 7, 10)
    witness = tuple(encoding[v] for v in (a,b,c,w,d1))
    linear_encodings = tuple(encoding[v] for v in coeff)
    terms = tuple(mul(co, wi) for co, wi in zip(linear_encodings, witness))
    quadratic = mul(witness[1], witness[4])
    f = quadratic
    for term in terms:
        f = add(f, term)
    assert f == (2, -1, -7, -5)
    assert evaluate(f) == -68 and evaluate(f) % N == 0

    witness_norm_sq = sum(norm_sq(x) for x in witness)
    beta_sq = Fraction(801, 100)
    assert witness_norm_sq == 8 and witness_norm_sq < beta_sq
    n = k = ell = 1
    M = n + (3+ell)*k
    linear_norm_sq = Fraction(M*D, 2)
    # S=sqrt((Md/2)*beta^2)+beta^2/2 < q. Compare exact rationals.
    margin = Q - beta_sq/2
    exact_gap = margin**2 - linear_norm_sq*beta_sq
    assert margin > 0 and exact_gap > 0
    assert exact_gap == Fraction(32401,40000)

    g = centered(f, Q)
    assert g == (2, -1, 6, -5)
    assert evaluate(g) == -16 and evaluate(g) % N == 1
    assert all((x-y) % Q == 0 for x,y in zip(f,g))
    assert max(abs(x) for x in f) < Q

    # Reviewer's representative-independent ambiguity, d=2, q=181, M=5.
    assert is_prime(181) and 19*19 % 181 == 180
    assert 11*11 % 181 == (-6*10) % 181
    assert 11*11 % 5 != (-6*10) % 5
    assert (-6)**2 + 10**2 <= 242
    assert Fraction(181-121)**2 > 5*242

    # Existing Figure 5 omission: a valid nonzero residual in ker(phi).
    x = (-1,0,1,0)       # Enc(3)=X^2-1
    enc9 = (0,0,0,-1)   # Enc(9)=-X^3
    h = add(mul(x,x), tuple(-z for z in enc9))
    assert h == (0,0,-2,1) and evaluate(h) == 0
    assert any(z % 101 for z in h)

    result = {
        'encoding_table': encoding,
        'honest_instance': {'d':D,'N':N,'q':Q,'n':n,'k':k,'l':ell,
                            'A':A,'B':B,'C':C,'w':w,'a':a,'b':b,'c':c,'d1':d1},
        'challenges': {'phi':phi,'alpha':alpha,'beta':beta_challenge,
                       'gamma':gamma,'delta':delta},
        'linear_coefficients': coeff,
        'linear_coefficient_encodings': linear_encodings,
        'witness_encodings': witness,
        'linear_product_terms': terms,
        'quadratic_product_term': quadratic,
        'witness_norm_squared': witness_norm_sq,
        'beta_squared': str(beta_sq),
        'exact_positive_squared_margin': str(exact_gap),
        'S_decimal_for_display_only': sqrt(float(linear_norm_sq*beta_sq))+float(beta_sq/2),
        'integer_residual': f,'centered_residue':g,
        'integer_evaluation':evaluate(f),'centered_evaluation':evaluate(g),
        'target_residues': [evaluate(f)%N,evaluate(g)%N],
        'all_assertions_passed': True,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
