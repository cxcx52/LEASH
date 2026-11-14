"""Independent schoolbook polynomial checks of public aggregation certificates.

Only finite-field/root-count arithmetic; no cryptographic prover or randomness.
"""
from itertools import product
from math import isqrt
from pathlib import Path
import json


def trim(a, q):
    out = [x % q for x in a]
    while out and out[-1] == 0:
        out.pop()
    return out


def add(a, b, q):
    out = [0]*max(len(a), len(b))
    for i,x in enumerate(a):
        out[i] += x
    for i,x in enumerate(b):
        out[i] += x
    return trim(out,q)


def mul(a, b, q):
    if not a or not b:
        return []
    out = [0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j] += x*y
    return trim(out,q)


def mod(a, f, q):
    a = trim(a,q)
    f = trim(f,q)
    inv = pow(f[-1],-1,q)
    while len(a) >= len(f):
        shift = len(a)-len(f)
        c = a[-1]*inv % q
        for j,x in enumerate(f):
            a[j+shift] = (a[j+shift]-c*x) % q
        a = trim(a,q)
    return a


def power(a, exponent, f, q):
    result = [1]
    while exponent:
        if exponent & 1:
            result = mod(mul(result,a,q),f,q)
        a = mod(mul(a,a,q),f,q)
        exponent >>= 1
    return result


def main():
    root = Path(__file__).resolve().parents[1]
    certificate = json.loads((root/'work/core_aggregation_field_certificate.json').read_text())
    q = certificate['q']
    assert q == 4294967197
    assert all(q % divisor for divisor in range(2,isqrt(q)+1))
    f = certificate['modulus_coefficients_ascending']
    assert f == [2,1,0,0,0,0,1]
    z = [0,1]
    value = z
    for i in range(1,7):
        value = power(value,q,f,q)
        if i in (2,3):
            item = certificate['frobenius_gcd_checkpoints'][str(i)]
            assert value == item['frobenius_remainder']
            residual = add(value,[0,-1],q)
            bezout = add(mul(item['bezout_residual'],residual,q),
                         mul(item['bezout_modulus'],f,q),q)
            assert bezout == [1]
    assert value == z == certificate['final_frobenius_remainder']
    assert int(certificate['field_order']) == q**6
    # q has order 32 modulo 128, so Phi_128 has two degree-32 factors.
    assert pow(q,32,128) == 1
    assert all(pow(q,t,128) != 1 for t in (1,2,4,8,16))

    # Scalar coordinate powers in F_9 = F_3[U]/(U^2+1).
    qsmall, fsmall = 3,[1,0,1]
    assert all((x*x+1) % 3 for x in range(3))
    small_scalar_cases = 0
    for coefficients in product(range(3),repeat=4):
        if not any(coefficients):
            continue
        degree = max(i for i,x in enumerate(coefficients) if x)
        roots = 0
        for point in product(range(3),repeat=2):
            powers = [power(list(point),i,fsmall,3) for i in range(4)]
            coordinates = [sum(coefficients[j]*(powers[j][i] if i<len(powers[j]) else 0)
                               for j in range(4)) % 3 for i in range(2)]
            horner = []
            for coefficient in reversed(coefficients):
                horner = mod(add(mul(horner,list(point),3),[coefficient],3),fsmall,3)
            assert trim(coordinates,3) == horner
            roots += not horner
            small_scalar_cases += 1
        assert roots <= degree

    # R_3=F_3[X]/(X^4+1), product of two irreducible quadratic fields.
    # Include a zero divisor explicitly; nonzero ring residuals need not be units.
    ring_modulus = [1,0,0,0,1]
    factor1, factor2 = [2,1,1],[2,2,1]
    assert mul(factor1,factor2,3) == ring_modulus
    for factor in (factor1,factor2):
        assert all(sum(c*pow(x,i,3) for i,c in enumerate(factor)) % 3 for x in range(3))
    coefficient_set = ([],[1],[0,1],[0,0,1],[0,0,0,1],factor1)
    small_ring_cases = 0
    max_roots = 0
    for coeffs in product(coefficient_set,repeat=3):
        if not any(coeffs):
            continue
        degree = max(i for i,c in enumerate(coeffs) if c)
        roots = 0
        for point in product(range(3),repeat=4):
            evaluation = []
            for coefficient in reversed(coeffs):
                evaluation = mod(add(mul(evaluation,list(point),3),coefficient,3),ring_modulus,3)
            roots += not evaluation
            small_ring_cases += 1
        assert roots <= degree*9
        max_roots = max(max_roots,roots)

    degree_sum_source160 = (2**27+166+1024-1)+6*(1024-1)
    degree_sum_source187 = (2**27+193+1024-1)+6*(1024-1)
    ring_degree_sum = (102+6-1)+6*(45+6-1)
    assert degree_sum_source160 == 134225055
    assert degree_sum_source187 == 134225082
    assert ring_degree_sum == 407
    result = {
        'scope':'Public field certificate and algebraic fingerprints only',
        'independent_degree6_certificate_verified':True,
        'modulus_coefficients_ascending':f,
        'q_prime_by_trial_division':True,
        'crt_order_mod128':32,
        'small_scalar_coordinate_evaluations':small_scalar_cases,
        'small_ring_evaluations_including_zero_divisors':small_ring_cases,
        'largest_small_ring_root_count':max_roots,
        'seven_layer_scalar_degree_sum_native160':degree_sum_source160,
        'seven_layer_scalar_degree_sum_fingerprint187':degree_sum_source187,
        'seven_layer_ring_degree_sum':ring_degree_sum,
        'scalar_point_wire_bits_per_layer':6*32,
        'ring_point_wire_bits_per_layer':64*32,
        'seven_layer_aggregation_point_wire_bits':7*(6+64)*32,
        'all_checks_passed':True,
    }
    (root/'work/core_aggregation_fingerprint_peer_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
