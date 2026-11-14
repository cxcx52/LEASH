"""Optional T=31 filtered challenges: statistical certificates only.

No production CSPRNG, challenge sampling loop, or cryptographic prover is supplied.
The unfiltered cube profiles remain unchanged.
"""

import json
from fractions import Fraction

from labrador_repair.challenges import (
    exact_operator_norm_below,
    filtered_challenge_profile,
)


if __name__ == "__main__":
    profile = filtered_challenge_profile(4294967197)
    assert profile["operator_norm_strictly_below"] == 31
    assert profile["acceptance_probability_strictly_greater_than"] == Fraction(9, 16)
    assert profile["expected_candidate_draws_strictly_less_than"] == Fraction(16, 9)
    assert exact_operator_norm_below((0,) * 64, 31)
    assert exact_operator_norm_below((2,) + (0,) * 63, 31)
    assert not exact_operator_norm_below((2,) * 64, 31)
    profile["exact_norm_examples_passed"] = True
    # Serialize the large exact integer as a decimal string for JSON readers
    # whose default number type cannot preserve 45-digit integers.
    profile["cardinality_lower_bound_inclusive"] = str(
        profile["cardinality_lower_bound_inclusive"])
    print(json.dumps(profile, indent=2, default=str))
