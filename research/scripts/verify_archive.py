"""Check archival bytes, linked model inputs, and exact path/payload records.

This verifies provenance and mathematical ledger consistency, not security.
It performs no Sage model run and no lattice computation.
"""

import hashlib
import json
from pathlib import Path

from joint_parameter_search import verify_path
from joint_energy_parameter_search import verify_saved_result
from parameter_feasibility_checks import transcript_ledger


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
    print(json.dumps({
        'scope': 'Archive-byte and exact-ledger verification; not security certification',
        'archived_source_files_checked': len(manifest['files']),
        'cross_file_model_hashes_match': True,
        'greedy_cube_bits': 1592448,
        'joint_cube_bits': 1521536,
        'joint_energy_bits': 1471680,
        'energy_outer_rank9_bits': 1270976,
        'all_checks_passed': True,
    }, indent=2))


if __name__ == '__main__':
    main()
