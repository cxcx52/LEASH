"""Same-domain exact Pareto search for the E104/T30 bounded-energy profile.

Uses the existing deterministic cap/encoding library and Pareto implementation.
It preserves the old cube result and constructs no lattice/prover instances.
"""

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from time import perf_counter

import parameter_feasibility_checks as caps
import fixed_energy_challenge_checks as energy
import joint_parameter_search as old

Q = old.Q
SCHEDULE = old.SCHEDULE
INNER_CAP = old.INNER_CAP
OUTER_CAP = old.OUTER_CAP
ENERGY_CAP = 104
OPERATOR_CAP = 30
GAMMA_FACTOR = F(9)
ACCEPTANCE = F(2, 3)


def challenge_certificate():
    total = energy.ball_count(64, ENERGY_CAP)
    assert total == 20905094450944450994971371210796521612779265
    bad = energy.ball_bad_bound(ENERGY_CAP, F(4, 5), OPERATOR_CAP, 12, F(933, 1000))
    assert bad < 1-ACCEPTANCE
    count_lower = 2*total//3+1
    assert count_lower == 13936729633962967329980914140531014408519511
    moments = energy.raw_ball_moments(ENERGY_CAP)
    v0, g, vu = moments['v0'], moments['g0'], moments['energy_variance']
    assert (9-v0)**2 > 24*g and v0 < F(25, 16)
    assert vu/(2*64**2) < F(1, 16)**2
    assert F(26, 16)*F(39, 8) == F(507, 64) < 9 and F(31, 8)**2 > 15
    statistical = 128*(F(sum(r+2 for r in SCHEDULE), count_lower)
                       + F(7, 2**164)+F(7, Q**6)+F(7, Q**32)+F(1, 2**160))
    assert statistical < F(1, 2**128)
    honest_layer = F(479, 528)
    assert 2*honest_layer**7 > 1
    assert caps.unit_cube_parameter_certificate(64, Q)
    return dict(raw_ball_count=total, cardinality_lower_bound=count_lower,
                energy_cap=ENERGY_CAP, operator_threshold=OPERATOR_CAP,
                raw_ball_acceptance_strict_lower=str(ACCEPTANCE),
                gamma_squared_factor=str(GAMMA_FACTOR),
                full_Q128_statistical_bound=str(statistical),
                full_Q128_statistical_below_2_minus_128=True,
                honest_layer_acceptance_strict_lower=str(honest_layer),
                honest_seven_layer_acceptance_strict_lower=str(honest_layer**7),
                expected_complete_attempts_below_two=True)


def rebuild(n, beta, index, base, t1, t2):
    return caps.core_cap(Q, 64, n, SCHEDULE[index], 24, beta, base, t1, t2,
                         operator_bound=OPERATOR_CAP, recursive=index < 6,
                         fold_failure=F(1, 16), honest_threshold=640,
                         gamma_squared_factor=GAMMA_FACTOR)


def feasible(row):
    return (row['jl_modulus_condition'] and row['standard_integer_msis_nontrivial']
            and row['outer_msis_bound'] <= OUTER_CAP
            and row['inner_weak_msis_bound'] <= INNER_CAP
            and row['inner_gram_msis_bound'] <= INNER_CAP)


def candidate_rows(state, index):
    for base in (2, 4, 8, 16, 32, 64, 128, 256):
        nominal = caps.digits_for(Q, base)
        for t1 in sorted({max(2, nominal+offset) for offset in (-1, 0, 1)}):
            for t2 in range(2, 20):
                row = rebuild(state.n, state.beta, index, base, t1, t2)
                if not feasible(row):
                    continue
                row['level'] = index+1
                if index < 6:
                    old.pairing(row, SCHEDULE[index+1])
                yield row


def verify_path(path):
    """Rebuild every norm/length, enforce the same finite domain and radius caps."""
    assert len(path) == 7
    n, beta = 37450, 16384
    assert F(16, 3)*beta*beta < Q
    assert 2*max(2**25, 3*2**25) < Q
    for index, row in enumerate(path):
        assert row['level'] == index+1
        assert row['n'] == n and row['beta'] == beta and row['r'] == SCHEDULE[index]
        assert row['b'] in (2, 4, 8, 16, 32, 64, 128, 256)
        nominal = caps.digits_for(Q, row['b'])
        assert row['t1'] in {max(2, nominal+offset) for offset in (-1, 0, 1)}
        assert 2 <= row['t2'] <= 19
        rebuilt = rebuild(n, beta, index, row['b'], row['t1'], row['t2'])
        assert all(row[key] == value for key, value in rebuilt.items())
        assert feasible(row)
        if index < 6:
            old.pairing(rebuilt, SCHEDULE[index+1])
            assert all(row[key] == rebuilt[key] for key in
                       ('next_n', 'next_r', 'nu', 'mu', 'next_padded_ring_length'))
            assert row['next_r'] == 2*row['nu']+row['mu']
            assert row['next_n']*row['nu'] >= n
            assert row['next_n']*row['mu'] >= row['auxiliary_ring_length']
            n, beta = row['next_n'], row['target_beta']


def verify_saved_result(saved):
    """Profile and whole-path validator for the separate pure-cost driver."""
    expected = dict(q=Q, d=64, H=640, T=OPERATOR_CAP, energy_cap=ENERGY_CAP,
                    raw_challenge_family='uniform squared-energy ball',
                    f='1/16', a='2/3', gamma_squared_factor='9',
                    kappa=24, outer_rank=16, r=list(SCHEDULE))
    assert saved['fixed_parameters'] == expected
    assert saved['domain'] == dict(bases=[2, 4, 8, 16, 32, 64, 128, 256],
                                  t1_offsets=[-1, 0, 1], t2_min=2, t2_max=19)
    assert saved['radius_caps'] == dict(inner_weak=INNER_CAP, inner_gram=INNER_CAP,
                                      outer=OUTER_CAP)
    assert saved['challenge_certificate'] == challenge_certificate()
    verify_path(saved['layers'])
    assert saved['best_payload'] == caps.transcript_ledger(saved['layers'], outer_rank=16)


def replay_old_choices(old_path):
    old.verify_path(old_path)
    rows = []
    n, beta = 37450, 16384
    for index, old_row in enumerate(old_path):
        row = rebuild(n, beta, index, old_row['b'], old_row['t1'], old_row['t2'])
        row['level'] = index+1
        if index < 6:
            old.pairing(row, SCHEDULE[index+1])
        assert row['n'] == old_row['n']
        for key in ('beta', 'gamma_ceiling', 'target_beta', 'actual_B',
                    'outer_msis_bound', 'inner_weak_msis_bound', 'inner_gram_msis_bound'):
            assert row[key] <= old_row[key]
        assert feasible(row)
        rows.append(row)
        if index < 6:
            n, beta = row['next_n'], row['target_beta']
    verify_path(rows)
    return rows


def run(old_result_path):
    old.small_skyline_check()
    certificate = challenge_certificate()
    old_saved = json.loads(old_result_path.read_text(encoding='utf-8'))
    old_path = old_saved['layers']
    old.verify_path(old_path)
    old_payload = caps.transcript_ledger(old_path, outer_rank=16)
    assert old_payload == old_saved['best_payload']
    assert old_payload['total_bits'] == 1521536
    replay = replay_old_choices(old_path)
    replay_payload = caps.transcript_ledger(replay, outer_rank=16)
    assert replay_payload['total_bits'] <= old_payload['total_bits']
    best_path, best_payload = tuple(replay), replay_payload
    states = [old.State(37450, 16384, 0, ())]
    history = []
    for index in range(7):
        start = perf_counter()
        unique = {}
        feasible_transitions = 0
        for state in states:
            accumulated = state.round_bits+old.round_bits(state.beta)
            for row in candidate_rows(state, index):
                feasible_transitions += 1
                path = state.path+(row,)
                if index == 6:
                    payload = caps.transcript_ledger(path, outer_rank=16)
                    assert payload['round_bits'] == accumulated
                    if payload['total_bits'] < best_payload['total_bits']:
                        best_path, best_payload = path, payload
                else:
                    key = (row['next_n'], row['target_beta'], accumulated)
                    if key not in unique:
                        unique[key] = old.State(*key, path)
        next_states = old.skyline(unique.values()) if index < 6 else []
        summary = dict(level=index+1, input_states=len(states),
                       feasible_transitions=feasible_transitions,
                       unique_successor_states=len(unique),
                       pareto_successor_states=len(next_states),
                       pareto_frontier=[dict(n=s.n, beta=s.beta, round_bits=s.round_bits)
                                        for s in next_states],
                       seconds=perf_counter()-start)
        history.append(summary)
        print(json.dumps(summary), flush=True)
        states = next_states
    verify_path(best_path)
    assert best_payload['total_bits'] <= replay_payload['total_bits'] <= old_payload['total_bits']
    root = Path(__file__).resolve().parents[1]
    sources = [root/'scripts'/'parameter_feasibility_checks.py',
               root/'scripts'/'joint_parameter_search.py',
               root/'scripts'/'joint_energy_parameter_search.py',
               root/'scripts'/'fixed_energy_challenge_checks.py',
               root/'proofs'/'fixed_energy_challenge_exploration.md', old_result_path.resolve()]
    result = dict(
        scope='Exact same-domain arithmetic payload optimum; no security certification',
        fixed_parameters=dict(q=Q, d=64, H=640, T=OPERATOR_CAP, energy_cap=ENERGY_CAP,
            raw_challenge_family='uniform squared-energy ball', f='1/16', a='2/3',
            gamma_squared_factor='9', kappa=24, outer_rank=16, r=list(SCHEDULE)),
        domain=dict(bases=[2, 4, 8, 16, 32, 64, 128, 256], t1_offsets=[-1, 0, 1], t2_min=2, t2_max=19),
        radius_caps=dict(inner_weak=INNER_CAP, inner_gram=INNER_CAP, outer=OUTER_CAP),
        challenge_certificate=certificate,
        old_cube_same_domain_optimum=old_payload,
        old_choices_recomputed_under_energy_profile=replay_payload,
        old_choices_energy_layers=replay,
        best_payload=best_payload,
        saved_bits_versus_old_cube=old_payload['total_bits']-best_payload['total_bits'],
        saved_bits_versus_replayed_old_choices=replay_payload['total_bits']-best_payload['total_bits'],
        layers=list(best_path), search_history=history,
        source_hashes={str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    verify_saved_result(result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old-result', type=Path, default=Path('work/joint_parameter_search.json'))
    parser.add_argument('--output', type=Path, default=Path('work/joint_energy_parameter_search.json'))
    args = parser.parse_args()
    result = run(args.old_result)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(best_payload=result['best_payload'],
                         saved_bits_versus_old_cube=result['saved_bits_versus_old_cube'])))
