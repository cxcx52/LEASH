"""Exact certificates for a binary-source random-evaluation fingerprint.

Pure finite-field arithmetic and communication accounting. This is neither
a cryptographic protocol implementation nor a prover or attack experiment.
"""

import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path


def poly_mod(a, modulus):
    d = modulus.bit_length() - 1
    while a.bit_length() - 1 >= d:
        a ^= modulus << (a.bit_length() - 1 - d)
    return a


def poly_gcd(a, b):
    while b:
        a, b = b, poly_mod(a, b)
    return a


def mul(a, b, modulus):
    answer = 0
    degree = modulus.bit_length() - 1
    while b:
        if b & 1:
            answer ^= a
        b >>= 1
        a <<= 1
        if a >> degree:
            a ^= modulus
    return answer


def prime_factors(n):
    result = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            result.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        result.append(n)
    return result


def irreducibility_certificate(modulus):
    degree = modulus.bit_length() - 1
    assert degree >= 2 and modulus & 1
    checkpoints = {degree // p for p in prime_factors(degree)}
    value = 2
    gcds = {}
    remainders = {}
    for i in range(1, degree + 1):
        value = mul(value, value, modulus)
        if i in checkpoints:
            remainders[str(i)] = str(value)
            gcds[str(i)] = poly_gcd(value ^ 2, modulus)
    return {
        'degree': degree,
        'modulus_integer': str(modulus),
        'exponents': [i for i in range(degree + 1) if (modulus >> i) & 1],
        'proper_subfield_frobenius_remainders': remainders,
        'proper_subfield_gcds': gcds,
        'final_frobenius_remainder': str(value),
        'irreducible': value == 2 and all(g == 1 for g in gcds.values()),
    }


def evaluate_binary(bits, t, modulus):
    answer = 0
    for bit in reversed(bits):
        answer = mul(answer, t, modulus) ^ bit
    return answer


def coordinate_rows(t, length, modulus):
    degree = modulus.bit_length() - 1
    rows = [[] for _ in range(degree)]
    power = 1
    for _ in range(length):
        for i in range(degree):
            rows[i].append((power >> i) & 1)
        power = mul(power, t, modulus)
    return rows


def small_field_checks():
    checked_pairs = 0
    checked_polynomials = 0
    for modulus in (0b111, 0b1011, 0b10011):
        cert = irreducibility_certificate(modulus)
        assert cert['irreducible']
        degree = cert['degree']
        length = min(7, (1 << degree) - 1)
        for code in range(1 << length):
            bits = [(code >> j) & 1 for j in range(length)]
            roots = 0
            for t in range(1 << degree):
                value = evaluate_binary(bits, t, modulus)
                rows = coordinate_rows(t, length, modulus)
                observed = sum((sum(a*b for a, b in zip(row, bits)) & 1) << i
                               for i, row in enumerate(rows))
                assert value == observed
                roots += value == 0
                checked_pairs += 1
            if code:
                assert roots <= code.bit_length() - 1
            else:
                assert roots == 1 << degree
            checked_polynomials += 1
    # A reducible quotient would invalidate the field root argument.
    assert not irreducibility_certificate(0b10101)['irreducible']
    return checked_pairs, checked_polynomials


def main():
    # Deterministic public-parameter search; no secret/random field data.
    degree = 187
    cert = None
    for exponents in combinations(range(1, 32), 3):
        polynomial = (1 << degree) | 1
        for exponent in exponents:
            polynomial |= 1 << exponent
        trial = irreducibility_certificate(polynomial)
        if trial['irreducible']:
            cert = trial
            break
    assert cert is not None, 'No irreducible pentanomial in the searched family'
    pairs, polynomials = small_field_checks()
    n = k = 1 << 25
    length = 3 * k
    error = Fraction(length - 1, 1 << degree)
    assert error < Fraction(1, 1 << 160)
    assert Fraction(length - 1, 1 << (degree - 1)) > Fraction(1, 1 << 160)
    even_values = (3*k // 2) - (-n // 2) + 1
    width = (even_values - 1).bit_length()
    assert even_values == (1 << 26) + 1 and width == 27
    result = {
        'scope': 'Exact algebra and source-message accounting; no SNARK/security-level claim',
        'irreducibility': cert,
        'small_exhaustive_pairs': pairs,
        'small_polynomials': polynomials,
        'residual_length': length,
        'error_numerator': error.numerator,
        'error_denominator': str(error.denominator),
        'error_strictly_below_2^-160': True,
        'minimum_degree_for_this_root_bound': degree,
        'baseline_challenge_bits': 160 * length,
        'fingerprint_challenge_bits': degree,
        'fingerprint_byte_aligned_challenge_bytes': (degree + 7) // 8,
        'baseline_scalar_reply_bits_32': 160 * 32,
        'fingerprint_scalar_reply_bits_32': degree * 32,
        'baseline_even_index_reply_bits': 160 * width,
        'fingerprint_even_index_reply_bits': degree * width,
        'added_target_scalar_equations': degree - 160,
        'added_witness_coordinates': 0,
        'all_checks_passed': True,
    }
    output = Path(__file__).resolve().parents[1] / 'work' / 'binary_fingerprint_checks.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
