"""Exact E104/T30/Gamma^2=9*d*beta^2 parameter certificates.

No sampling, prover, complete recursive schedule, or hardness estimate is supplied.
"""

import json
from fractions import Fraction as F

from labrador_repair.energy import bounded_energy_profile, energy_shell_count


if __name__ == "__main__":
    q = 4294967197
    profile = bounded_energy_profile(q)
    lower = profile["cardinality_lower_bound_inclusive"]
    total_statistical = 128*(F(198, lower)+F(7, 2**164)+F(7, q**6)
                             +F(7, q**32)+F(1, 2**160))
    assert total_statistical < F(1, 2**128)
    shell = energy_shell_count(64, 71)
    assert shell < 3*2**128
    profile["conditional_Q128_statistical_upper"] = total_statistical
    profile["statistical_components_assumed"] = {
        "seven_layer_sum_r_plus_two": 198,
        "JL_per_layer": "2^-164", "scalar_per_layer": "q^-6",
        "ring_per_layer": "q^-32", "source": "2^-160", "restart_cap": 128,
    }
    profile["computational_losses_included"] = False
    profile["energy_71_shell_count_exact"] = shell
    profile["energy_71_current_challenge_bound_obstruction"] = "N<3*2^128; limitation of (r+2)/N, not an attack"
    # Keep exact counts intact in JSON consumers with floating-point numbers.
    for key in ("raw_ball_cardinality_exact", "cardinality_lower_bound_inclusive",
                "energy_71_shell_count_exact"):
        profile[key] = str(profile[key])
    print(json.dumps(profile, indent=2, default=str))
