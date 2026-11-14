"""Pure cost-model screening with an unmodified pinned lattice-estimator.

Run with Sage's Python. This script does not create or solve lattice instances,
run BKZ, produce short vectors, or implement a cryptographic prover.
"""
import argparse
import hashlib
from fractions import Fraction as F
from functools import lru_cache
import json
import math
from pathlib import Path
import subprocess
import sys

import parameter_feasibility_checks as parameters

PIN='53da5982597709ba0fdf94ea37a84d822310fd84'
Q=4294967197


def optimum_dimension(rows,columns,radius):
    """Maximize (ln L-n ln q/D)/(D-1), not an attack implementation."""
    volume=rows*math.log(Q)
    target=math.log(radius)
    peak=(volume+math.sqrt(volume*(volume-target)))/target
    lo=rows+1
    candidates={lo,columns,max(lo,min(columns,math.floor(peak))),
                max(lo,min(columns,math.ceil(peak)))}
    return max(candidates,key=lambda dim:(target-volume/dim)/(dim-1))


@lru_cache(None)
def ln_delta(block):
    if block==40:
        return math.log(1.01295)
    return (math.log(block/(2*math.pi*math.e))
            +math.log(math.pi*block)/block)/(2*(block-1))


def crt_candidate(rows,columns,energy):
    if energy<1:
        return None
    volume=rows*math.log(Q)
    target=math.log(energy)/2
    for block in range(40,min(columns,65536)+1):
        factor=ln_delta(block)
        stationary=math.sqrt(volume/factor)
        lower=max(rows+1,block)
        dimensions={min(columns,max(lower,math.floor(stationary))),
                    min(columns,max(lower,math.ceil(stationary)))}
        dim=min(dimensions,key=lambda x:(x-1)*factor+volume/x)
        if (dim-1)*factor+volume/dim<=target:
            return dim,block
    return None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--estimator',type=Path,
                        required=True, help='Clean external estimator checkout at the pinned commit')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--path-input',type=Path,
                        help='Exact fixed-profile joint_parameter_search output to rescreen')
    parser.add_argument('--ranks',default='16,20,24,28,32,40,48,64')
    parser.add_argument('--conditional-gamma-factor',type=F,default=None,
                        help='Unverified concentration override; reported as conditional')
    parser.add_argument('--fold-profile',choices=['markov','paired-fourth','centered-fourth','bounded-energy'],
                        default='markov')
    args=parser.parse_args()
    if args.conditional_gamma_factor is not None and args.fold_profile!='markov':
        raise ValueError('Choose a reviewed profile or a conditional override, not both')
    gamma_factor=args.conditional_gamma_factor
    proof_hash=None
    fixed_honest_profile=dict(H=640,fold_rejection='1/16',T=34,
                             acceptance_lower='901/1024',slack_squared='16/3')
    if args.fold_profile=='bounded-energy':
        if args.path_input is None:
            raise ValueError('Bounded-energy screening requires a fully verified saved joint path')
        from joint_energy_parameter_search import challenge_certificate
        challenge_certificate()
        proof=Path(__file__).resolve().parents[1]/'proofs'/'fixed_energy_challenge_exploration.md'
        proof_hash=hashlib.sha256(proof.read_bytes()).hexdigest()
        gamma_factor=F(9)
        fixed_honest_profile.update(T=30,acceptance_lower='2/3',energy_cap=104,
                                   raw_challenge_family='uniform squared-energy ball')
    elif args.fold_profile!='markov':
        proof=Path(__file__).resolve().parents[1]/'proofs'/'filtered_fourth_moment.md'
        proof_hash=hashlib.sha256(proof.read_bytes()).hexdigest()
        gamma_factor=F(12) if args.fold_profile=='paired-fourth' else F(21,2)
        assert parameters.certified_acceptance(64,34)>=F(901,1024)
        if gamma_factor==12:
            assert F(648704,4505)<144 and F(2191,512)**2>15
        else:
            assert F(321024,4505)<F(289,4)
            assert F(861,144160)<F(1,144) and 15<F(31,8)**2
            assert F(325,32)<F(21,2)
    root=args.estimator.resolve()
    git=['git','-c','safe.directory='+str(root),'-C',str(root)]
    revision=subprocess.check_output(git+['rev-parse','HEAD'],text=True).strip()
    dirty=subprocess.check_output(git+['status','--porcelain','-uno'],text=True).strip()
    if revision!=PIN or dirty:
        raise ValueError('Requires clean pinned estimator '+PIN)
    sys.path.insert(0,str(root))
    from sage.all import ZZ,sqrt,log,oo
    from sage.version import version
    from estimator import SIS
    from estimator.sis_lattice import SISLattice
    from estimator.reduction import ADPS16,MATZOV,ChaLoy21,RC
    models={'core_classical_0292':ADPS16('classical'),
            'core_quantum_0265':ADPS16('quantum'),
            'core_quantum_0257':ChaLoy21(),
            'matzov_classical':MATZOV(nn='classical'),
            'matzov_quantum_depth_width':MATZOV(nn='quantum')}

    def costs(rows,columns,radius,dimension=None):
        if not (rows<columns and 1<radius<Q):
            return {'status':'outside screened small-radius underdetermined regime'}
        dim=dimension or optimum_dimension(rows,columns,radius)
        params=SIS.Parameters(n=rows,m=columns,q=Q,length_bound=radius,norm=2)
        output={}
        for name,model in models.items():
            cost=SISLattice.cost_euclidean(params,d=dim,red_cost_model=model)
            output[name]=None if cost['rop']==oo else float(log(cost['rop'],2))
        block=int(cost['beta'])
        return dict(n=rows,m=columns,dimension=dim,block_size=block,
                    delta=float(cost['delta']),log2_cost=output,
                    matzov_within_documented_fit=block<=1024,
                    status='finite heuristic model fit' if output['core_classical_0292'] is not None
                           else 'no fit at this dimension in pinned model')

    profiles=[]
    if args.path_input is not None:
        saved=json.loads(args.path_input.read_text(encoding='utf-8'))
        fixed=saved['fixed_parameters']
        assert fixed['q']==Q and fixed['d']==64 and fixed['kappa']==24
        saved_path=saved['layers']
        if args.fold_profile=='bounded-energy':
            from joint_energy_parameter_search import verify_saved_result
            verify_saved_result(saved)
        elif args.fold_profile=='centered-fourth':
            from joint_parameter_search import verify_path
            verify_path(saved_path)
        else:
            raise ValueError('Saved joint path requires centered-fourth or bounded-energy profile')
        ranks=[24]
    else:
        saved_path=None
        ranks=list(map(int,args.ranks.split(',')))
    for kappa in ranks:
        profile=saved_path if saved_path is not None else parameters.recursion_screen(
            kappa=kappa,operator_bound=34,acceptance=F(901,1024),fold_failure=F(1,16),
            honest_threshold=640,gamma_squared_factor=gamma_factor)
        complete=len(profile)==7 and 'actual_B' in profile[-1]
        result=dict(inner_rank=kappa,outer_ranks=16,complete_arithmetic_path=complete,
                    layers=profile)
        if not complete:
            profiles.append(result)
            continue
        result['payload']=parameters.transcript_ledger(profile,outer_rank=16)
        screened=[]
        for row in profile:
            pairs=row['r']*(row['r']+1)//2
            roles=[('inner',kappa,row['n'],max(row['inner_weak_msis_bound'],row['inner_gram_msis_bound'])),
                   ('outer_first',16,row['r']*row['t1']*kappa+pairs*row['t2'],row['outer_msis_bound']),
                   ('outer_second',16,pairs*row['t1'],row['outer_msis_bound'])]
            for role,ring_rows,ring_columns,radius in roles:
                n,m=64*ring_rows,64*ring_columns
                normal=costs(n,m,ZZ(radius))
                energy=radius*radius//Q
                candidate=crt_candidate(n//2,m,energy)
                if candidate is None:
                    crt=dict(reduced_energy=energy,n=n//2,m=m,
                        status='no GSA fit through min(m,65536)' if energy
                               else 'zero reduced energy: no nonzero integer vector')
                else:
                    dimension,block=candidate
                    crt=costs(n//2,m,sqrt(ZZ(energy)),dimension)
                    crt['reduced_energy']=energy
                    assert crt['block_size']==block, (crt,block)
                screened.append(dict(level=row['level'],role=role,ring_rows=ring_rows,
                                     ring_columns=ring_columns,radius=radius,
                                     generic=normal,single_crt=crt))
        result['screens']=screened
        profiles.append(result)
    output=dict(scope='Pure heuristic cost models; no lattice solving or security certification',
                q=Q,d=64,estimator_commit=revision,sage_version=version,
                norm='coefficient Euclidean; standard nonzero integer SIS',
                fixed_honest_profile=fixed_honest_profile,
                fold_profile=args.fold_profile,
                path_input_sha256=hashlib.sha256(args.path_input.read_bytes()).hexdigest()
                    if args.path_input is not None else None,
                gamma_squared_factor=str(gamma_factor) if gamma_factor is not None else None,
                fourth_moment_proof_sha256=proof_hash,
                completeness_status=('proved '+args.fold_profile+' bound; arithmetic profile only')
                    if args.conditional_gamma_factor is None else
                    'conditional on independent concentration theorem; not certified by this screen',
                upstream_fixed_delta_block=int(RC.beta(1.00444)),profiles=profiles)
    encoded=json.dumps(output,indent=2,allow_nan=False)
    if args.output:
        args.output.write_text(encoded+'\n',encoding='utf-8')
    else:
        print(encoded)


if __name__=='__main__':
    main()
