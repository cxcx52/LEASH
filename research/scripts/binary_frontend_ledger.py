"""Native binary-front-end arithmetic and optional pinned cost-model ledger.

No prover, transcript construction, lattice instance, or lattice solver. The
model mode calls only the pinned SIS cost functions, with explicit dimensions.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from math import isqrt
from pathlib import Path
import subprocess
import sys

from computational_parameter_screen import PIN,optimum_dimension

Q=4294967197
D=64
N=K=2**25
ELL=160


def ceil_sqrt(value):
    root=isqrt(value)
    return root+(root*root<value)


def arithmetic():
    half=N+3*K
    raw_rings=2*half//D
    actual_norm_squared=F(16,3)*2*half
    assert actual_norm_squared<Q and 6*K<Q
    assert 2*max(N,3*K)<Q
    chunks,chunk_length=14,37450
    per_block_rings=N//D
    pad_per_block=chunks*chunk_length-per_block_rings
    assert pad_per_block==12 and raw_rings+8*pad_per_block==112*chunk_length
    even_values=(N+3*K)//2+1
    even_bits=(even_values-1).bit_length()
    interval_bits=(N+3*K).bit_length()
    assert even_bits==27 and interval_bits==28
    exponent_field_bits=187
    assert F(3*K-1,2**exponent_field_bits)<F(1,2**160)
    parity_ell=160
    parity_rings=N+(3+parity_ell)*K
    # Necessary part of the parity frontend sufficient lift already fails:
    # beta_actual^2=(16/3) M exceeds q, before adding the linear term.
    assert F(16,3)*parity_rings>Q
    research=Path(__file__).resolve().parents[1]
    path_file=research/'work'/'joint_energy_parameter_search.json'
    saved=json.loads(path_file.read_text())
    from joint_energy_parameter_search import verify_saved_result
    from parameter_feasibility_checks import transcript_ledger
    verify_saved_result(saved)
    core_payload_bits=transcript_ledger(saved['layers'],outer_rank=9)['total_bits']
    assert core_payload_bits==1270976
    projection_rows=[]
    for index,row in enumerate(saved['layers']):
        coordinates=row['r']*row['n']*D
        entries=1024*coordinates
        scalar_constraints=half+4+1+ELL+1 if index==0 else 0
        ring_constraints=6+96 if index==0 else 24+3+2*9
        projection_rows.append(dict(level=index+1,r=row['r'],n=row['n'],
            witness_coefficients=coordinates,ternary_projection_entries=entries,
            projection_two_bit_wire_bits=2*entries,
            projection_entropy_and_prefix_expected_bits=F(3,2)*entries,
            input_constant_term_constraints_without_public_pins=scalar_constraints,
            input_full_ring_constraints_at_source_rank6_outer_rank9=ring_constraints,
            scalar_aggregation_challenge_bits=6*(scalar_constraints+1024)*32,
            ring_aggregation_challenge_bits=(ring_constraints+6)*D*32,
            final_fold_challenge_three_bit_coordinate_wire_bits=row['r']*D*3))
    projection_totals={key:sum(row[key] for row in projection_rows) for key in
        ('ternary_projection_entries','projection_two_bit_wire_bits',
         'projection_entropy_and_prefix_expected_bits','scalar_aggregation_challenge_bits',
         'ring_aggregation_challenge_bits','final_fold_challenge_three_bit_coordinate_wire_bits')}
    projection_totals['explicit_fixed_encoding_core_verifier_bits']=sum(
        projection_totals[key] for key in ('projection_two_bit_wire_bits',
        'scalar_aggregation_challenge_bits','ring_aggregation_challenge_bits',
        'final_fold_challenge_three_bit_coordinate_wire_bits'))
    assert all(value.denominator==1 for row in projection_rows for value in row.values()
               if isinstance(value,F))
    for row in projection_rows:
        for key,value in row.items():
            if isinstance(value,F):row[key]=int(value)
    projection_totals={key:int(value) for key,value in projection_totals.items()}
    return dict(q=Q,d=D,n_including_constant=N,k=K,ell=ELL,
        native_source_commitment_count=1,source_ring_columns=half//D,
        source_scalar_columns=half,source_collision_squared_radius=half,
        source_collision_conservative_integer_radius=ceil_sqrt(half),
        source_collision_infinity_bound=1,
        raw_witness_ring_length=raw_rings,raw_witness_coefficient_length=2*half,
        honest_squared_norm=2*half,extracted_squared_norm=str(actual_norm_squared),
        padded_witness_ring_length=112*chunk_length,
        first_core_rank=chunk_length,first_core_multiplicity=112,
        source_blocks=8,chunks_per_block=chunks,padding_rings_per_block=pad_per_block,
        total_padding_rings=8*pad_per_block,padding_zero_full_ring_constraints=8*pad_per_block,
        conjugacy_scalar_equations=half,
        other_constant_term_equations_without_public_pins=4+1+ELL+1,
        total_constant_term_equations_without_public_pins=half+4+1+ELL+1,
        scalar_reply_interval=[-N,3*K],scalar_reply_even_values=even_values,
        scalar_reply_bits_plain_residue=32,scalar_reply_bits_shifted_interval=interval_bits,
        scalar_reply_bits_even_interval=even_bits,
        source_reply_bits_plain_residue=ELL*32,
        source_reply_bits_shifted_interval=ELL*interval_bits,
        source_reply_bits_even_interval=ELL*even_bits,
        explicit_verifier_independent_challenge_bits=ELL*3*K,
        explicit_verifier_independent_challenge_GiB=F(ELL*3*K,8*2**30).__str__(),
        native_statistical_bound=str(F(1,2**ELL)),
        core_verifier_explicit_challenge_ledger=dict(
            path_file_sha256=hashlib.sha256(path_file.read_bytes()).hexdigest(),
            source_rank_assumed=6,outer_rank_assumed=9,public_pin_count_beyond_constant=0,
            general_H_row_count=0,rows=projection_rows,totals=projection_totals),
        parity_affine=dict(ell=parity_ell,ring_witness_length=parity_rings,
            honest_squared_norm=parity_rings,commitment_count=2,
            first_commitment_ring_columns=half,second_commitment_ring_columns=ELL*K,
            statistical_bound=str(F(2,2**parity_ell)),
            compatible_with_current_shape=False,current_q_fails_sufficient_lift=True),
        optional_power_challenge_arithmetic=dict(status='independently reviewed source-only variant; baseline remains independent ell160',
            proof='proofs/binary_fingerprint_frontend.md',
            peer_review='proofs/binary_fingerprint_peer_review.md',
            field_bits=exponent_field_bits,aggregation_rows=exponent_field_bits,
            nonzero_polynomial_degree_bound=3*K-1,
            statistical_bound=str(F(3*K-1,2**exponent_field_bits)),
            challenge_bits=exponent_field_bits,
            reply_bits_plain_residue=exponent_field_bits*32,
            reply_bits_even_interval=exponent_field_bits*even_bits,
            extra_core_scalar_aggregation_challenge_bits=(exponent_field_bits-ELL)*6*32,
            source_rank6_prover_bits=6*D*32+exponent_field_bits*even_bits,
            source_rank6_prover_byte_framed_bytes=(6*D*32+exponent_field_bits*even_bits+7)//8,
            source_rank6_ball_core_total_prover_raw_bits=core_payload_bits+6*D*32+exponent_field_bits*even_bits,
            source_rank6_ball_core_total_prover_byte_framed_bytes=core_payload_bits//8+(6*D*32+exponent_field_bits*even_bits+7)//8,
            source_plus_core_explicit_verifier_raw_bits=projection_totals['explicit_fixed_encoding_core_verifier_bits']
                +(exponent_field_bits-ELL)*6*32+exponent_field_bits))


def cost_models(args,ledger):
    root=args.estimator.resolve()
    git=['git','-c','safe.directory='+str(root),'-C',str(root)]
    revision=subprocess.check_output(git+['rev-parse','HEAD'],text=True).strip()
    dirty=subprocess.check_output(git+['status','--porcelain','-uno'],text=True).strip()
    assert revision==PIN and not dirty
    sys.path.insert(0,str(root))
    from sage.all import ZZ,sqrt,log,oo
    from sage.version import version
    from estimator import SIS
    from estimator.sis_lattice import SISLattice
    from estimator.reduction import ADPS16,MATZOV,ChaLoy21
    models={'core_classical_0292':ADPS16('classical'),
            'core_quantum_0265':ADPS16('quantum'),
            'core_quantum_0257':ChaLoy21(),
            'matzov_classical':MATZOV(nn='classical'),
            'matzov_quantum_depth_width':MATZOV(nn='quantum')}
    research=Path(__file__).resolve().parents[1]
    previous_file=research/'work'/'outer_rank_parameter_screen.json'
    previous=json.loads(previous_file.read_text())
    assert previous['estimator_commit']==PIN
    threshold=previous['baseline_cube_minima']
    current_ball=next(p for p in previous['profiles'] if p['profile']=='energy_ball')
    current_ball_rank9=next(r for r in current_ball['ranks'] if r['outer_rank']==9)
    ball_threshold=current_ball_rank9['core_model_minima']
    out=[]
    radius=ZZ(ledger['source_collision_conservative_integer_radius'])
    for rank in range(1,17):
        rows,columns=D*rank,ledger['source_scalar_columns']
        dimension=optimum_dimension(rows,columns,radius)
        params=SIS.Parameters(n=rows,m=columns,q=Q,length_bound=radius,norm=2)
        values={}
        for name,model in models.items():
            cost=SISLattice.cost_euclidean(params,d=dimension,red_cost_model=model)
            values[name]=None if cost['rop']==oo else float(log(cost['rop'],2))
        block=int(cost['beta'])
        commit_bits=rank*D*32
        size=commit_bits+ledger['source_reply_bits_even_interval']
        cube_pass=all(values[name] is not None and values[name]>=threshold[name]['log2_cost']
                      for name in models)
        ball_pass=all(values[name] is not None and values[name]>=ball_threshold[name]['log2_cost']
                      for name in models)
        # The reviewed single-CRT lifting test has zero energy in this profile.
        assert int(radius*radius)//Q==0
        item=dict(source_ring_rank=rank,scalar_rows=rows,scalar_columns=columns,
            conservative_radius=int(radius),dimension=dimension,block_size=block,
            delta=float(cost['delta']),log2_cost=values,
            matzov_within_documented_fit=block<=1024,
            preserves_old_cube_minima=cube_pass,preserves_current_ball_minima=ball_pass,
            commitment_bits=commit_bits,prover_frontend_bits_even_interval=size,
            prover_frontend_bits_plain_residue=commit_bits+ELL*32,
            ball_core_plus_frontend_bits_even_interval=current_ball_rank9['payload']['total_bits']+size,
            dense_source_CRS_bytes=rank*ledger['source_ring_columns']*D*4,
            single_crt_reduced_energy=0)
        out.append(item)
        print(json.dumps(dict(rank=rank,block=block,cube_pass=cube_pass,ball_pass=ball_pass,
                              log2_cost=values)),flush=True)
    return dict(estimator_commit=revision,sage_version=version,
        previous_cost_record_sha256=hashlib.sha256(previous_file.read_bytes()).hexdigest(),
        norm='coefficient Euclidean standard nonzero integer SIS; conservative ceil radius',
        thresholds_cube=threshold,thresholds_ball=ball_threshold,
        minimum_rank_preserving_cube=min(r['source_ring_rank'] for r in out if r['preserves_old_cube_minima']),
        minimum_rank_preserving_ball=min(r['source_ring_rank'] for r in out if r['preserves_current_ball_minima']),
        rows=out)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models',action='store_true',help='Requires pinned Sage Python')
    parser.add_argument('--estimator',type=Path,help='Clean external pinned estimator checkout; required with --models')
    parser.add_argument('--output',type=Path,default=Path('work/binary_frontend_ledger.json'))
    args=parser.parse_args()
    if args.models and args.estimator is None:
        parser.error('--models requires an explicit --estimator path')
    result=dict(scope='Arithmetic and optional heuristic costs only; no security certification',arithmetic=arithmetic())
    if args.models:result['cost_screen']=cost_models(args,result['arithmetic'])
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
