"""Sage-only public extension-field construction and irreducibility certificate.

Pure polynomial arithmetic; no commitments, witnesses, prover, or randomness.
"""
from pathlib import Path
import json

from sage.all import GF, PolynomialRing, ZZ, power_mod
from sage.version import version


def coefficients(poly):
    return [int(x) for x in poly.list()]


def main():
    q = ZZ(4294967197)
    assert q.is_prime()
    ring = PolynomialRing(GF(q), 'Z')
    z = ring.gen()
    modulus = None
    for constant in range(1, 1025):
        candidate = z**6+z+constant
        if candidate.is_irreducible():
            modulus = candidate
            break
    assert modulus is not None
    checkpoints = {}
    value = z
    for exponent in range(1, 7):
        value = power_mod(value, q, modulus)
        if exponent in (2, 3):
            residual = value-z
            gcd_value, left, right = residual.xgcd(modulus)
            assert gcd_value == 1
            assert left*residual+right*modulus == 1
            checkpoints[str(exponent)] = dict(
                frobenius_remainder=coefficients(value),
                gcd=coefficients(gcd_value),
                bezout_residual=coefficients(left),
                bezout_modulus=coefficients(right),
            )
    assert value == z
    field = GF(q**6, name='u', modulus=modulus)
    assert field.degree() == 6 and field.order() == q**6
    result = {
        'scope':'Public field arithmetic certificate only; independent of R_q',
        'sage_version':version,
        'q':int(q),
        'q_is_prime':True,
        'extension_degree':6,
        'modulus_coefficients_ascending':coefficients(modulus),
        'modulus_display':str(modulus),
        'frobenius_gcd_checkpoints':checkpoints,
        'final_frobenius_remainder':coefficients(value),
        'field_order':str(q**6),
        'irreducible':True,
    }
    root = Path(__file__).resolve().parents[1]
    (root/'work/core_aggregation_field_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
