"""Exact integer-ring operations used in the lifting repair."""


def centered(value, modulus):
    if modulus < 1:
        raise ValueError("positive modulus required")
    return (value+modulus//2) % modulus-modulus//2


def encode(value, degree):
    """Centered non-adjacent form in Z[X]/(X^degree+1)."""
    if degree < 2 or degree & (degree-1):
        raise ValueError("degree must be a power of two >=2")
    z = centered(value, 2**degree+1)
    out = [0]*degree
    i = 0
    while z:
        digit = 0 if z % 2 == 0 else 2-z % 4
        if i >= degree:
            raise ArithmeticError("NAF exceeded the proven degree bound")
        out[i] = digit
        z = (z-digit)//2
        i += 1
    return tuple(out)


def evaluate(poly, point=2):
    value = 0
    for coefficient in reversed(poly):
        value = value*point+coefficient
    return value


def negacyclic_multiply(a, b):
    if len(a) != len(b) or not a:
        raise ValueError("nonempty equal-length polynomials required")
    d = len(a)
    out = [0]*d
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i+j) % d] += x*y*(1 if i+j < d else -1)
    return tuple(out)


def gcd_mod(a, b, q):
    """Monic polynomial gcd for tests over a prime field."""
    def trim(p):
        p = [x % q for x in p]
        while p and not p[-1]:
            p.pop()
        return p
    a, b = trim(a), trim(b)
    while b:
        r = a[:]
        while len(r) >= len(b):
            coefficient = r[-1]*pow(b[-1], -1, q) % q
            shift = len(r)-len(b)
            for i in range(len(b)):
                r[shift+i] = (r[shift+i]-coefficient*b[i]) % q
            r = trim(r)
        a, b = b, r
    if not a:
        return ()
    inverse = pow(a[-1], -1, q)
    return tuple(x*inverse % q for x in a)
