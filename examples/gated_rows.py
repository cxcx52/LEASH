"""Exact probability-model checks for the accept-gated extraction lemma.

Finite distribution calculations supplement the universal proof in
docs/unknown-gap-extraction.md.
"""
from fractions import Fraction
from itertools import product
import json


def check_late_final_rows():
    grid = (Fraction(0), Fraction(1, 2), Fraction(1))
    counts = {}
    low_density_nonzero_rows = 0
    for n in (3, 4, 5):
        abort_coin = Fraction(1, n)
        counts[n] = 0
        for acceptance in product(grid, repeat=n):
            p = sum(acceptance, Fraction()) / n
            work = Fraction()
            abort_mass = Fraction()
            success_mass = Fraction()
            for a_c in acceptance:
                if not a_c:
                    continue
                # Unnormalized mass that this challenge passes the gate.
                gate_mass = a_c / n
                distinct_success = p - a_c / n
                stop_probability = distinct_success + (1-distinct_success)*abort_coin
                assert 0 < stop_probability <= 1
                work += gate_mass / stop_probability
                abort_mass += gate_mass * (1-distinct_success)*abort_coin / stop_probability
                success_mass += gate_mass * distinct_success / stop_probability
            assert work <= 1/(1-abort_coin)
            assert abort_mass <= abort_coin
            assert success_mass + abort_mass == p
            if 0 < p < abort_coin:
                low_density_nonzero_rows += 1
            counts[n] += 1
    return counts, low_density_nonzero_rows


def check_deterministic_rows():
    count = 0
    for n in range(3, 257):
        a = Fraction(1, n)
        for accepted_count in range(1, n+1):
            p = Fraction(accepted_count, n)
            stop = (p-a)+(1-p+a)*a
            assert stop == p*(1-a)+a*a
            assert stop - p*(1-p+a) == (p-a)**2
            assert p/stop <= 1/(1-a)
            assert p*a*(1-p+a)/stop <= a
            count += 1
    return count


def main():
    counts, low_rows = check_late_final_rows()
    deterministic_count = check_deterministic_rows()
    print(json.dumps({
        'all_assertions_passed': True,
        'late_final_counts_by_challenge_size': counts,
        'late_final_total': sum(counts.values()),
        'late_final_positive_density_below_one_over_N': low_rows,
        'deterministic_rows_checked': deterministic_count,
        'work_bound': '1/(1-1/N) per coordinate, including gate mass',
        'abort_mass_bound': '1/N per coordinate, including gate mass',
        'scope': 'finite arithmetic certificates; universal proof remains necessary'
    }, indent=2))


if __name__ == '__main__':
    main()
