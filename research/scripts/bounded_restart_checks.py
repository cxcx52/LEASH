"""Exact probability arithmetic for bounded complete-protocol restarts.

No prover, proof transcript, attack, or cryptographic protocol is implemented.
"""
from fractions import Fraction as F
from itertools import product
import json


def guaranteed_inverse_power_two(probability):
    assert 0 < probability <= 1
    # Largest integer b for which probability <= 2^-b, exactly.
    return (probability.denominator // probability.numerator).bit_length() - 1


def main():
    old_a = F(67, 132)**7
    candidate_new_a = F(479, 528)**7
    assert candidate_new_a > F(1, 2)
    count_lower = (9*5**64)//16 + 1
    q = 4294967197
    one_attempt_stat = (F(198, count_lower) + F(7, 2**164)
                        + F(7, q**6) + F(7, q**32) + F(1, 2**160))
    assert one_attempt_stat < F(1, 2**140)
    rows = []
    for attempts in (16, 32, 128, 1024):
        old_failure = (1-old_a)**attempts
        candidate_failure = (1-candidate_new_a)**attempts
        assert candidate_failure < F(1, 2**attempts)
        assert attempts*one_attempt_stat < F(attempts, 2**140)
        rows.append({
            "attempt_cap": attempts,
            "old_profile_failure_upper_display": float(old_failure),
            "old_profile_failure_guaranteed_bits": guaranteed_inverse_power_two(old_failure),
            "candidate_new_profile_failure_guaranteed_bits": guaranteed_inverse_power_two(candidate_failure),
            "candidate_new_profile_certified_less_than": f"2^-{attempts}",
            "restart_statistical_error_guaranteed_bits": guaranteed_inverse_power_two(attempts*one_attempt_stat),
            "old_profile_expected_attempt_upper_display": float((1-old_failure)/old_a),
            "candidate_new_profile_expected_attempt_upper_display": float((1-candidate_failure)/candidate_new_a)
        })

    # Finite probability-tree checks: state-dependent gate acceptance and
    # conditional extraction success. Output mass is supported on first gates.
    distributions = 0
    grid = (F(0), F(1, 2), F(1))
    for acceptance in product(grid, repeat=3):
        for conditional_extraction in product(grid, repeat=3):
            reach = F(1)
            accept_mass = witness_mass = lost_mass = expected_calls = F(0)
            for p, success in zip(acceptance, conditional_extraction):
                first_accept = reach*p
                output = first_accept*success
                assert output <= first_accept
                accept_mass += first_accept
                witness_mass += output
                lost_mass += first_accept-output
                expected_calls += reach
                reach *= 1-p
            assert accept_mass == 1-reach
            assert witness_mass == accept_mass-lost_mass
            assert expected_calls <= 3
            distributions += 1
    print(json.dumps({
        "old_profile_one_attempt_lower": str(old_a),
        "candidate_new_profile_one_attempt_lower": str(candidate_new_a),
        "new_profile_greater_than_one_half_exact": True,
        "new_profile_status": "norm/profile independently reviewed; no numerical MSIS hardness certificate",
        "single_attempt_statistical_error_guaranteed_bits": guaranteed_inverse_power_two(one_attempt_stat),
        "restart_rows": rows,
        "finite_probability_tree_cases": distributions,
        "note": "All displayed decisive inequalities are checked with Fraction; decimals are presentation only."
    }, indent=2))


if __name__ == "__main__":
    main()
