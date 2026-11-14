"""Check archival bytes, linked model inputs, and exact path/payload records.

This verifies provenance and mathematical ledger consistency, not security.
It performs no Sage model run and no lattice computation.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from joint_parameter_search import verify_path
from joint_energy_parameter_search import verify_saved_result
from parameter_feasibility_checks import transcript_ledger
from binary_fingerprint_checks import irreducibility_certificate
from core_aggregation_fingerprint_peer_checks import add, mul, power


def main():
    root = Path(__file__).resolve().parents[1]
    results = root/'notes'/'parameter-results'
    def read(name):
        return json.loads((results/name).read_text(encoding='utf-8'))
    def digest(name):
        return hashlib.sha256((results/name).read_bytes()).hexdigest()
    manifest = read('archive-manifest.json')
    for entry in manifest['files']:
        archived = root/entry['archive_relative']
        actual = hashlib.sha256(archived.read_bytes()).hexdigest()
        assert actual == entry['archive_sha256'], entry['archive_relative']
        if entry['archive_relative'].endswith('.json'):
            assert entry['byte_identical']
            assert actual == entry['source_sha256']
    cube = read('joint-cube.json')
    ball = read('joint-energy.json')
    verify_path(cube['layers'])
    verify_saved_result(ball)
    assert cube['best_payload']['total_bits'] == 1521536
    assert ball['best_payload']['total_bits'] == 1471680
    models = {'cube': read('joint-cube-models.json'),
              'energy_ball': read('joint-energy-models.json')}
    paths = {'cube': ('joint-cube.json', cube),
             'energy_ball': ('joint-energy.json', ball)}
    pin = '53da5982597709ba0fdf94ea37a84d822310fd84'
    for name, model in models.items():
        path_file, saved = paths[name]
        assert model['estimator_commit'] == pin
        assert model['path_input_sha256'] == digest(path_file)
        assert model['profiles'][0]['layers'] == saved['layers']
        assert model['profiles'][0]['payload'] == transcript_ledger(saved['layers'], outer_rank=16)
        assert len(model['profiles'][0]['screens']) == 21
    outer = read('outer-ranks.json')
    assert outer['estimator_commit'] == pin
    expected_bits = {'cube': 1320832, 'energy_ball': 1270976}
    model_files = {'cube': 'joint-cube-models.json', 'energy_ball': 'joint-energy-models.json'}
    for profile in outer['profiles']:
        name = profile['profile']
        path_file, saved = paths[name]
        assert profile['path_sha256'] == digest(path_file)
        assert profile['original_model_sha256'] == digest(model_files[name])
        assert profile['path'] == saved['layers']
        assert profile['minimum_passing_outer_rank'] == 9
        assert profile['selected_parameters']['outer_rank'] == 9
        assert profile['selected_target_full_ring_equations'] == 45
        selected = transcript_ledger(saved['layers'], outer_rank=9)
        assert selected == profile['selected_payload']
        assert selected['total_bits'] == expected_bits[name]
        for row in profile['ranks']:
            assert row['preserves_all_five_cube_baselines'] == (row['outer_rank'] >= 9)
    greedy = read('centered-fourth.json')
    rank24 = next(p for p in greedy['profiles'] if p['inner_rank'] == 24)
    assert rank24['payload']['total_bits'] == 1592448

    # Native-source supplement: exact arithmetic and raw provenance links.
    native = read('native_binary_source_checks.json')
    assert native['all_assertions_passed']
    assert native['source_original_coefficient_count'] == 2**27
    assert native['source_commitment_ring_columns'] == 2**21
    assert native['source_collision_squared_radius'] == 2**27
    assert native['source_collision_radius_ceiling'] == 11586
    assert Fraction(native['full_extracted_squared_cap']) == Fraction(2**32, 3)
    assert native['padded_witness_ring_length'] == 112*37450 == 4194400
    assert native['per_block_ring_padding'] == 12
    assert native['scalar_reply_width'] == 27
    assert native['source_scalar_reply_bytes'] == 540
    assert native['source_verifier_challenge_bits'] == 160*3*2**25

    fingerprint = read('binary_fingerprint_checks.json')
    assert fingerprint['all_checks_passed']
    assert fingerprint['irreducibility']['exponents'] == [0, 1, 2, 20, 187]
    modulus = sum(1 << i for i in (0, 1, 2, 20, 187))
    assert irreducibility_certificate(modulus) == fingerprint['irreducibility']
    root_error = Fraction(fingerprint['error_numerator'], int(fingerprint['error_denominator']))
    assert root_error == Fraction(3*2**25-1, 2**187) < Fraction(1, 2**160)
    assert fingerprint['fingerprint_challenge_bits'] == 187
    assert fingerprint['fingerprint_even_index_reply_bits'] == 5049
    assert fingerprint['added_target_scalar_equations'] == 27
    assert fingerprint['added_witness_coordinates'] == 0
    field_peer = read('binary_fingerprint_peer_checks.json')
    assert field_peer['all_checks_passed']
    assert Fraction(*field_peer['source_error']) == root_error
    assert field_peer['exhaustive_native_parity_instances'] == 16384
    assert field_peer['native_scalar_rows'] == 49152
    assert field_peer['packed_source_reply_bytes_rounded_once'] == 632

    source_record = read('binary_frontend_ledger.json')
    source = source_record['arithmetic']
    assert source == read('binary_frontend_arithmetic.json')['arithmetic']
    assert source['source_ring_columns'] == 2**21
    assert source['source_collision_squared_radius'] == 2**27
    assert source['native_source_commitment_count'] == 1
    source_core = source['core_verifier_explicit_challenge_ledger']
    assert source_core['path_file_sha256'] == digest('joint-energy.json')
    totals = source_core['totals']
    projection_entries = sum(1024*row['r']*row['n']*64 for row in ball['layers'])
    assert totals['projection_two_bit_wire_bits'] == 2*projection_entries == 580126375936
    assert totals['scalar_aggregation_challenge_bits'] == 192*(2**27+166+7*1024)
    assert totals['ring_aggregation_challenge_bits'] == 2048*(108+6*51) == 847872
    assert totals['final_fold_challenge_three_bit_coordinate_wire_bits'] == 192*sum(row['r'] for row in ball['layers']) == 35328
    assert totals['explicit_fixed_encoding_core_verifier_bits'] == 605898471040
    wire_peer = read('native_frontend_ledger_peer_checks.json')
    assert wire_peer['all_checks_passed']
    assert wire_peer['native_source_and_core_verifier_fixed_wire_bits'] == 622004598400
    assert wire_peer['fingerprint_added_first_scalar_challenge_bits'] == 27*6*32 == 5184
    optional = source['optional_power_challenge_arithmetic']
    assert optional['source_rank6_ball_core_total_prover_raw_bits'] == 1270976+6*64*32+187*27 == 1288313
    assert optional['source_rank6_ball_core_total_prover_byte_framed_bytes'] == (1288313+7)//8 == 161040
    assert optional['source_plus_core_explicit_verifier_raw_bits'] == 605898471040+5184+187 == 605898476411
    assert wire_peer['fingerprint_source_and_core_verifier_fixed_wire_bits'] == optional['source_plus_core_explicit_verifier_raw_bits']

    source_models = source_record['cost_screen']
    assert source_models['estimator_commit'] == pin
    assert source_models['previous_cost_record_sha256'] == digest('outer-ranks.json')
    assert source_models['thresholds_cube'] == outer['baseline_cube_minima']
    energy_outer = next(p for p in outer['profiles'] if p['profile'] == 'energy_ball')
    energy_outer9 = next(r for r in energy_outer['ranks'] if r['outer_rank'] == 9)
    assert source_models['thresholds_ball'] == energy_outer9['core_model_minima']
    assert source_models['minimum_rank_preserving_cube'] == 5
    assert source_models['minimum_rank_preserving_ball'] == 6
    assert len(source_models['rows']) == 16
    selected_source = next(row for row in source_models['rows'] if row['source_ring_rank'] == 6)
    assert selected_source['ball_core_plus_frontend_bits_even_interval'] == 1287584
    assert selected_source['ball_core_plus_frontend_bits_even_interval']//8 == 160948
    assert selected_source['preserves_current_ball_minima']

    # Optional ordinary aggregation has its own verifier law and error ledger.
    field_certificate = read('core_aggregation_field_certificate.json')
    q = 4294967197
    modulus6 = field_certificate['modulus_coefficients_ascending']
    assert field_certificate['q'] == q and modulus6 == [2, 1, 0, 0, 0, 0, 1]
    frobenius = [0, 1]
    for degree in range(1, 7):
        frobenius = power(frobenius, q, modulus6, q)
        if degree in (2, 3):
            checkpoint = field_certificate['frobenius_gcd_checkpoints'][str(degree)]
            assert frobenius == checkpoint['frobenius_remainder']
            residual = add(frobenius, [0, -1], q)
            bezout = add(mul(checkpoint['bezout_residual'], residual, q),
                         mul(checkpoint['bezout_modulus'], modulus6, q), q)
            assert bezout == [1]
    assert frobenius == [0, 1] == field_certificate['final_frobenius_remainder']
    assert int(field_certificate['field_order']) == q**6
    aggregation_peer = read('core_aggregation_fingerprint_peer_checks.json')
    assert aggregation_peer['all_checks_passed']
    assert aggregation_peer['independent_degree6_certificate_verified']
    assert aggregation_peer['crt_order_mod128'] == 32
    assert aggregation_peer['seven_layer_scalar_degree_sum_fingerprint187'] == 134225082
    assert aggregation_peer['seven_layer_ring_degree_sum'] == 407
    assert aggregation_peer['seven_layer_aggregation_point_wire_bits'] == 15680
    aggregation = read('ordinary_power_aggregation_checks.json')
    assert aggregation['scalar_field_nonzero_polynomials'] == 358
    assert aggregation['CRT_nonzero_polynomial_cases'] == 16272
    count_lower = ball['challenge_certificate']['cardinality_lower_bound']
    for variant in aggregation['profiles']:
        source_rows = variant['source_aggregation_rows']
        assert source_rows in (160, 187)
        degree_sum = 134225055 + source_rows - 160
        source_error = Fraction(1, 2**160) if source_rows == 160 else root_error
        expected_stat = 128*(Fraction(198, count_lower)+Fraction(7, 2**164)
                            +Fraction(degree_sum, q**6)+Fraction(407, q**32)+source_error)
        assert Fraction(variant['Q128_total_statistical_bound']) == expected_stat < Fraction(1, 2**128)
        assert variant['scalar_degree_sum'] == degree_sum
        assert variant['ring_degree_sum'] == 407
        assert variant['core_explicit_verifier_bits'] == 580126375936+15680+35328 == 580126426944
        assert not variant['prover_payload_changed_by_core_aggregation']
    fully_fingerprinted = next(p for p in aggregation['profiles'] if p['source_aggregation_rows'] == 187)
    assert fully_fingerprinted['source_plus_core_explicit_verifier_raw_bits'] == 580126427131
    print(json.dumps({
        'scope': 'Archive-byte and exact-ledger verification; not security certification',
        'archived_source_files_checked': len(manifest['files']),
        'cross_file_model_hashes_match': True,
        'greedy_cube_bits': 1592448,
        'joint_cube_bits': 1521536,
        'joint_energy_bits': 1471680,
        'energy_outer_rank9_bits': 1270976,
        'native_complete_prover_bytes': 160948,
        'source_fingerprint_complete_prover_bytes': 161040,
        'source_fingerprint_challenge_bits': 187,
        'native_explicit_verifier_bits': 622004598400,
        'source_fingerprint_explicit_verifier_bits': 605898476411,
        'native_source_minimum_rank_matching_cube': 5,
        'native_source_minimum_rank_matching_energy': 6,
        'aggregation_fingerprint_explicit_verifier_bits': 580126427131,
        'aggregation_fingerprint_statistical_budget_below_2^-128': True,
        'all_checks_passed': True,
    }, indent=2))


if __name__ == '__main__':
    main()
