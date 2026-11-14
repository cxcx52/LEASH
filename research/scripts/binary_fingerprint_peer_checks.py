"""Independent exact arithmetic checks for the native source fingerprint.

This checks public finite-field algebra and small relation identities only. It
does not implement a prover, cryptographic randomness, or a forgery experiment.
The field multiplication below uses explicit convolution/reduction, independent
of the bit-serial multiplier in binary_fingerprint_checks.py.
"""

from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib
import json


def multiply(a, b, exponents):
    degree = max(exponents)
    convolution = [0] * (2 * degree - 1)
    for i in range(degree):
        for j in range(degree):
            convolution[i + j] ^= ((a >> i) & 1) & ((b >> j) & 1)
    for high in range(2 * degree - 2, degree - 1, -1):
        if convolution[high]:
            for exponent in exponents:
                convolution[high - degree + exponent] ^= 1
    assert not any(convolution[degree:])
    return sum(bit << i for i, bit in enumerate(convolution[:degree]))


def fingerprint(bits, t, exponents):
    powers = [1]
    for _ in range(1, len(bits)):
        powers.append(multiply(powers[-1], t, exponents))
    value = 0
    for bit, power in zip(bits, powers):
        if bit:
            value ^= power
    return value, powers


def polynomial_checks():
    pairs = 0
    polynomials = 0
    for exponents in ((2, 1, 0), (3, 1, 0), (4, 1, 0)):
        m = max(exponents)
        length = min(7, 2**m - 1)
        for bits in product((0, 1), repeat=length):
            roots = 0
            for t in range(2**m):
                value, powers = fingerprint(bits, t, exponents)
                coordinates = [sum(bit * ((power >> i) & 1)
                                   for bit, power in zip(bits, powers)) % 2
                               for i in range(m)]
                assert value == sum(bit << i for i, bit in enumerate(coordinates))
                roots += value == 0
                pairs += 1
            if any(bits):
                actual_degree = max(j for j, bit in enumerate(bits) if bit)
                assert roots <= actual_degree
            else:
                assert roots == 2**m
            polynomials += 1
    return pairs, polynomials


def native_parity_checks():
    # n=2,k=1; all three binary matrix rows, all original binary coordinates,
    # every t in F_8. Includes t=0 and all leading-zero residual cases.
    cases = 0
    scalar_rows = 0
    for entries in product((0, 1), repeat=6):
        matrices = (entries[:2], entries[2:4], entries[4:])
        for original in product((0, 1), repeat=5):
            abc, w = original[:3], original[3:]
            residual = [a ^ (sum(x * y for x, y in zip(row, w)) % 2)
                        for a, row in zip(abc, matrices)]
            for t in range(8):
                expected, powers = fingerprint(residual, t, (3, 1, 0))
                observed = 0
                for i in range(3):
                    challenge = [(power >> i) & 1 for power in powers]
                    delta = [sum(challenge[j] * matrices[j][column]
                                 for j in range(3)) % 2
                             for column in range(2)]
                    integer_reply = sum(x * y for x, y in zip(challenge, abc))
                    integer_reply -= sum(x * y for x, y in zip(delta, w))
                    assert -2 <= integer_reply <= 3
                    observed |= (integer_reply % 2) << i
                    # q=17 exceeds the complete interval span n+3k=5.
                    for transmitted in range(-2, 4):
                        if (transmitted - integer_reply) % 17 == 0:
                            assert transmitted == integer_reply
                    scalar_rows += 1
                assert observed == expected
                cases += 1
    return cases, scalar_rows


def main():
    pairs, polynomials = polynomial_checks()
    cases, scalar_rows = native_parity_checks()
    length = 3 * 2**25
    error = Fraction(length - 1, 2**187)
    assert error < Fraction(1, 2**160)
    assert Fraction(length - 1, 2**186) > Fraction(1, 2**160)
    assert Fraction(187 * length, 8 * 2**30) == Fraction(561, 256)
    assert 187 * 27 == 5049
    assert (187 * 27 + 7) // 8 == 632
    assert (160 * 27 + 7) // 8 == 540
    source = Path(__file__).resolve()
    result = {
        'scope': 'Independent public algebra checks; no protocol security claim',
        'checker_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'exhaustive_polynomial_evaluation_pairs': pairs,
        'exhaustive_binary_polynomials': polynomials,
        'exhaustive_native_parity_instances': cases,
        'native_scalar_rows': scalar_rows,
        'source_error': [error.numerator, error.denominator],
        'root_bound_below_2^-160': True,
        'dense_187_row_GiB': '561/256 = 2.19140625',
        'packed_source_reply_bits': 5049,
        'packed_source_reply_bytes_rounded_once': 632,
        'Sage_separate_check': {
            'polynomial_exponents': [187, 20, 2, 1, 0],
            'is_irreducible': True,
            'is_squarefree': True,
            'note': 'Independent Sage invocation recorded in peer review; not rerun by this script',
        },
        'all_checks_passed': True,
    }
    output = source.parents[1] / 'work' / 'binary_fingerprint_peer_checks.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
