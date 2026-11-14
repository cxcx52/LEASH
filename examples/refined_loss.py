"""Abstract rational loss certificates with explicitly hypothetical eta inputs.

No estimator output is converted into an advantage, and no extractor is run.
"""

from fractions import Fraction as F
import json

from labrador_repair.extraction_bounds import (
    collision_loss_envelope, finite_bad_mass_upper, finite_witness_lower,
    gated_upper_root_certified, gated_witness_lower, simple_gated_root_upper,
)


if __name__ == "__main__":
    r, n = 8, 65536
    epsilon, kappa = F(3, 4), F(1, 256)
    eta_0, eta_h, eta_y, eta_g, eta_e = (F(1, 2**32), F(1, 2**40),
                                       F(1, 2**42), F(1, 2**40), F(1, 2**40))
    h = collision_loss_envelope(r, eta_h, eta_y, eta_g)
    upper = simple_gated_root_upper(kappa, eta_0, h, F(1, 2**16), F(1, 2**12))
    assert gated_upper_root_certified(kappa, eta_0, h, upper)
    assert not gated_upper_root_certified(F(0), F(0), F(1, 8), F(0))
    gate_lower = gated_witness_lower(epsilon, kappa, r, n, eta_0, h, eta_e, root_upper=upper)
    delta, zeta = F(1, 64), F(1, 1024)
    # This is a SEPARATE finite-anchor illustration. In an application its eta
    # values must belong to that finite experiment; gate advantages do not transfer.
    finite_upper = finite_bad_mass_upper(delta, eta_0, h)
    finite_lower = finite_witness_lower(epsilon, kappa, delta, zeta, eta_0, h, eta_e)
    print(json.dumps({
        "scope": "Abstract mathematical certificates; supplied eta values are hypothetical",
        "not_inferred_from": "No lattice cost point, Core-SVP estimate or benchmark",
        "r": r, "N": n, "epsilon": epsilon, "kappa": kappa,
        "eta_0": eta_0, "eta_h": eta_h, "eta_y": eta_y, "eta_g": eta_g, "eta_E": eta_e,
        "H": h, "gated_root_upper": upper, "gated_witness_lower": gate_lower,
        "spurious_zero_rejected": True,
        "separate_finite_anchor_illustration": {
            "delta": delta, "zeta": zeta,
            "bad_High_mass_upper": finite_upper, "witness_lower": finite_lower,
            "premise": "The same numeric eta choices would need independent bounds for the finite anchor law",
        },
    }, indent=2, default=str))
