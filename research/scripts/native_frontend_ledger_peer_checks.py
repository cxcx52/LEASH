"""Independent exact sums for the native source/core verifier wire ledger."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json


def main():
    root = Path(__file__).resolve().parents[1]
    ledger = json.loads((root/'work/binary_frontend_peer_rerun.json').read_text())['arithmetic']
    saved = json.loads((root/'work/joint_energy_parameter_search.json').read_text())
    shape = ((112,37450),(33,5795),(15,1754),(8,877),(7,440),(5,440),(4,443))
    assert tuple((row['r'],row['n']) for row in saved['layers']) == shape
    q, d = 4294967197, 64
    assert q**5 < 2**160 <= q**6
    D = 2**27
    expected = []
    for i,(r,n) in enumerate(shape):
        variables = d*r*n
        scalar_inputs = D+166 if i == 0 else 0
        ring_inputs = 102 if i == 0 else 45
        projection_entries = 1024*variables
        expected.append({
            'level':i+1,
            'ternary_projection_entries':projection_entries,
            'projection_two_bit_wire_bits':projection_entries*2,
            'projection_entropy_and_prefix_expected_bits':projection_entries*3//2,
            'scalar_aggregation_challenge_bits':(scalar_inputs+1024)*(32*6),
            'ring_aggregation_challenge_bits':(ring_inputs+6)*(32*64),
            'final_fold_challenge_three_bit_coordinate_wire_bits':r*(3*64),
        })
    original = ledger['core_verifier_explicit_challenge_ledger']
    for i,row in enumerate(expected):
        for key,value in row.items():
            assert original['rows'][i][key] == value, (i,key,value,original['rows'][i][key])
    totals = {key:sum(row[key] for row in expected) for key in expected[0] if key != 'level'}
    for key,value in totals.items():
        assert original['totals'][key] == value
    # Independently partition the fixed-width total into main projection,
    # source conjugacy scalar terms, remaining scalar terms, ring terms, folds.
    independent_total = (2048*d*sum(r*n for r,n in shape)
                         +192*(D+166+7*1024)
                         +2048*(108+6*51)
                         +192*sum(r for r,n in shape))
    assert original['totals']['explicit_fixed_encoding_core_verifier_bits'] == independent_total
    native_source_bits = 160*3*2**25
    fingerprint_source_bits = 187
    extra_scalar_challenges = (187-160)*6*32
    assert extra_scalar_challenges == 5184
    assert totals['ring_aggregation_challenge_bits'] == 847872
    assert totals['final_fold_challenge_three_bit_coordinate_wire_bits'] == 35328
    assert F(native_source_bits,8*2**30) == F(15,8)
    core_prover_bits = 1270976
    source_commitment_bits = 6*64*32
    assert core_prover_bits+source_commitment_bits+187*27 == 1288313
    assert (1288313+7)//8 == 161040
    result = {
        'scope':'Exact wire-count peer review, not a cost-model or security-level check',
        'rows':expected,
        'totals':totals,
        'native_core_fixed_wire_bits':independent_total,
        'native_source_and_core_verifier_fixed_wire_bits':independent_total+native_source_bits,
        'fingerprint_added_first_scalar_challenge_bits':extra_scalar_challenges,
        'fingerprint_core_fixed_wire_bits':independent_total+extra_scalar_challenges,
        'fingerprint_source_and_core_verifier_fixed_wire_bits':independent_total+extra_scalar_challenges+fingerprint_source_bits,
        'fingerprint_complete_prover_byte_padded_bytes':161040,
        'fingerprint_complete_prover_KiB':str(F(161040,1024)),
        'audited_script_sha256':hashlib.sha256((root/'scripts/binary_frontend_ledger.py').read_bytes()).hexdigest(),
        'audited_fingerprint_proof_sha256':hashlib.sha256((root/'proofs/binary_fingerprint_frontend.md').read_bytes()).hexdigest(),
        'all_checks_passed':True,
    }
    (root/'work/native_frontend_ledger_peer_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
