"""Reproducible exact-predicate microbenchmark on energy-ball inputs.

This measures Python implementations, not a complete prover, security level,
or a population rejection probability. The RNG is only for benchmark fixtures.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from labrador_repair.challenges import exact_operator_norm_below
from labrador_repair.energy import energy_ball_count, energy_ball_unrank
from labrador_repair.fourier import certified_operator_norm_below


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--degree', type=int, default=64)
    parser.add_argument('--energy', type=int, default=104)
    parser.add_argument('--threshold', type=int, default=30)
    parser.add_argument('--samples', type=int, default=32)
    parser.add_argument('--seed', type=int, default=20261114)
    args = parser.parse_args()
    if args.samples < 1 or args.samples > 100000:
        parser.error('samples must be in 1..100000')
    if args.degree < 2 or args.degree > 256 or args.degree & (args.degree-1):
        parser.error('degree must be a power of two in 2..256')
    if not 0 <= args.energy <= 4 * args.degree or args.threshold < 1:
        parser.error('invalid energy or threshold')
    start = perf_counter()
    cardinality = energy_ball_count(args.degree, args.energy)
    count_seconds = perf_counter()-start
    rng = random.Random(args.seed)
    start = perf_counter()
    inputs = [energy_ball_unrank(args.degree, args.energy, rng.randrange(cardinality))
              for _ in range(args.samples)]
    input_seconds = perf_counter()-start
    input_bytes = json.dumps(inputs, separators=(',', ':')).encode('ascii')
    start = perf_counter()
    zero_result = certified_operator_norm_below((0,)*args.degree, args.threshold)
    cold_first_call_seconds = perf_counter()-start
    if not zero_result:
        raise RuntimeError('zero must satisfy a positive strict norm threshold')
    times = {'certified_fourier_seconds': 0.0, 'exact_spd_seconds': 0.0}
    paths = Counter()
    accepted = 0
    for index, coefficients in enumerate(inputs):
        answers = {}
        order = ('fourier', 'spd') if index % 2 == 0 else ('spd', 'fourier')
        for name in order:
            start = perf_counter()
            if name == 'fourier':
                answer, path = certified_operator_norm_below(
                    coefficients, args.threshold, with_path=True)
                times['certified_fourier_seconds'] += perf_counter()-start
                paths[path] += 1
            else:
                answer = exact_operator_norm_below(coefficients, args.threshold)
                times['exact_spd_seconds'] += perf_counter()-start
            answers[name] = answer
        if answers['fourier'] != answers['spd']:
            raise RuntimeError('independent exact predicates disagree at input '+str(index))
        accepted += answers['fourier']
    rss = None
    rss_status = 'unavailable on this platform'
    if sys.platform.startswith('linux'):
        import resource
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rss_status = 'Linux ru_maxrss in KiB; includes Python and entire child process'
    result = {
        'schema': 'labrador-kernel-benchmark/v1',
        'scope': 'Exact Python predicate microbenchmark; not complete proof verification or a security estimate',
        'configuration': vars(args),
        'rng': 'random.Random; deterministic public benchmark fixtures only',
        'raw_ball_cardinality_exact': str(cardinality),
        'fixture_sha256': hashlib.sha256(input_bytes).hexdigest(),
        'candidate_count': args.samples,
        'accepted_in_this_fixture': accepted,
        'all_predicate_decisions_match': True,
        'fourier_path_counts': dict(paths),
        'count_dp_seconds': count_seconds,
        'fixture_generation_seconds': input_seconds,
        'cold_first_fourier_call_seconds': cold_first_call_seconds,
        'cold_first_call_scope': 'Certified table/cache initialization and a zero-input query; excludes Python startup/imports',
        'warm_predicate_timings': times,
        'warm_spd_over_fourier_time_ratio': times['exact_spd_seconds']/times['certified_fourier_seconds'],
        'process_peak_rss_kib': rss,
        'rss_scope': rss_status,
        'comparison_scope': 'Both methods use the same exact SPD routine on Fourier fallback inputs; fallback agreement is not an independent implementation check',
        'complete_prover_implemented': False,
        'statistical_population_estimate_claimed': False,
    }
    print(json.dumps(result, indent=2))
    print('CHALLENGE_MEMBERSHIP_BENCHMARK_PASS')


if __name__ == '__main__':
    main()
