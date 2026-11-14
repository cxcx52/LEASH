"""Exact T34 and Gamma^2=(21/2)*d*beta^2 honest-fold certificate.

This example does not sample challenges or implement a cryptographic prover.
"""

import json
from fractions import Fraction as F

from labrador_repair.folding import filtered_folding_profile


if __name__ == "__main__":
    profile = filtered_folding_profile(4294967197)
    assert profile["gamma_squared_over_d_beta_squared"] == F(21, 2)
    assert profile["honest_fold_rejection_probability_upper"] == F(1, 16)
    challenge = profile["challenge_certificate"]
    assert challenge["operator_norm_strictly_below"] == 34
    assert challenge["acceptance_probability_strictly_greater_than"] == F(901, 1024)
    challenge["cardinality_lower_bound_inclusive"] = str(challenge["cardinality_lower_bound_inclusive"])
    print(json.dumps(profile, indent=2, default=str))
