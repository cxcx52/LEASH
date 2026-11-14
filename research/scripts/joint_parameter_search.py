"""Exact finite-domain payload search for the fixed repaired ordinary core.

Pure integer/Fraction arithmetic. No lattice instance or cryptographic prover is
constructed. Pareto pruning uses monotone state variables n, beta, round bits.
"""
import argparse
from dataclasses import dataclass
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from time import perf_counter

import parameter_feasibility_checks as caps

Q=4294967197
SCHEDULE=(112,33,15,8,7,5,4)
INNER_CAP=918564400
OUTER_CAP=168800


@dataclass(frozen=True)
class State:
    n:int
    beta:int
    round_bits:int
    path:tuple


def round_bits(beta):
    return 2*16*64*32+6*64*32+1024*caps.signed_bits(caps.ceil_sqrt(640*beta*beta))


def skyline(states):
    """All nondominated states, using a prefix-minimum Fenwick tree."""
    ordered=sorted(states,key=lambda x:(x.n,x.beta,x.round_bits))
    betas=sorted({state.beta for state in ordered})
    ranks={beta:index+1 for index,beta in enumerate(betas)}
    tree=[float('inf')]*(len(betas)+1)
    result=[]
    for state in ordered:
        index=ranks[state.beta]
        minimum=float('inf')
        query=index
        while query:
            minimum=min(minimum,tree[query])
            query-=query&-query
        if minimum<=state.round_bits:
            continue
        result.append(state)
        while index<len(tree):
            tree[index]=min(tree[index],state.round_bits)
            index+=index&-index
    return result


def pairing(row,next_r):
    choices=[]
    for nu in range(1,(next_r-1)//2+1):
        mu=next_r-2*nu
        next_n=max((row['n']+nu-1)//nu,(row['auxiliary_ring_length']+mu-1)//mu)
        choices.append((next_n,nu,mu))
    next_n,nu,mu=min(choices)
    row.update(next_n=next_n,next_r=next_r,nu=nu,mu=mu,
               next_padded_ring_length=next_n*next_r)


def candidate_rows(state,index):
    for base in (2,4,8,16,32,64,128,256):
        nominal=caps.digits_for(Q,base)
        for t1 in sorted({max(2,nominal+offset) for offset in (-1,0,1)}):
            for t2 in range(2,20):
                row=caps.core_cap(Q,64,state.n,SCHEDULE[index],24,state.beta,
                    base,t1,t2,operator_bound=34,recursive=index<6,
                    fold_failure=F(1,16),honest_threshold=640,gamma_squared_factor=F(21,2))
                if not(row['jl_modulus_condition'] and row['standard_integer_msis_nontrivial']
                    and row['outer_msis_bound']<=OUTER_CAP
                    and row['inner_weak_msis_bound']<=INNER_CAP
                    and row['inner_gram_msis_bound']<=INNER_CAP):
                    continue
                row['level']=index+1
                if index<6:
                    pairing(row,SCHEDULE[index+1])
                yield row


def verify_path(path):
    assert len(path)==7
    n,beta=37450,16384
    assert F(16,3)*beta*beta<Q
    assert 2*max(2**25,3*2**25)<Q
    for index,row in enumerate(path):
        assert row['n']==n and row['beta']==beta and row['r']==SCHEDULE[index]
        rebuilt=caps.core_cap(Q,64,n,SCHEDULE[index],24,beta,row['b'],row['t1'],row['t2'],
            operator_bound=34,recursive=index<6,fold_failure=F(1,16),honest_threshold=640,
            gamma_squared_factor=F(21,2))
        assert all(row[key]==value for key,value in rebuilt.items())
        assert row['inner_weak_msis_bound']<=INNER_CAP
        assert row['inner_gram_msis_bound']<=INNER_CAP and row['outer_msis_bound']<=OUTER_CAP
        if index<6:
            assert row['next_r']==2*row['nu']+row['mu']
            assert row['next_n']*row['nu']>=n
            assert row['next_n']*row['mu']>=row['auxiliary_ring_length']
            n,beta=row['next_n'],row['target_beta']


def small_skyline_check():
    # Independent quadratic dominance oracle with duplicate removal.
    triples={(n,b,c) for n in range(1,8) for b in range(1,9) for c in range(1,10)
             if (17*n+13*b+11*c)%19 in (0,1)}
    expected={x for x in triples if not any(y!=x and all(a<=b for a,b in zip(y,x)) for y in triples)}
    actual={(x.n,x.beta,x.round_bits) for x in skyline([State(*x,()) for x in triples])}
    assert actual==expected


def run():
    small_skyline_check()
    baseline=caps.recursion_screen(kappa=24,operator_bound=34,acceptance=F(901,1024),
        fold_failure=F(1,16),honest_threshold=640,gamma_squared_factor=F(21,2))
    verify_path(baseline)
    baseline_ledger=caps.transcript_ledger(baseline,outer_rank=16)
    states=[State(37450,16384,0,())]
    history=[]
    best_path=tuple(baseline)
    best_ledger=baseline_ledger
    for index in range(7):
        start=perf_counter()
        unique={}
        feasible=0
        for state in states:
            accumulated=state.round_bits+round_bits(state.beta)
            for row in candidate_rows(state,index):
                feasible+=1
                path=state.path+(row,)
                if index==6:
                    ledger=caps.transcript_ledger(path,outer_rank=16)
                    assert ledger['round_bits']==accumulated
                    if ledger['total_bits']<best_ledger['total_bits']:
                        best_path,best_ledger=path,ledger
                else:
                    key=(row['next_n'],row['target_beta'],accumulated)
                    if key not in unique:
                        unique[key]=State(*key,path)
        next_states=skyline(unique.values()) if index<6 else []
        summary=dict(level=index+1,input_states=len(states),feasible_transitions=feasible,
            unique_successor_states=len(unique),pareto_successor_states=len(next_states),
            seconds=perf_counter()-start)
        history.append(summary)
        print(json.dumps(summary),flush=True)
        states=next_states
    verify_path(best_path)
    assert best_ledger['total_bits']<=baseline_ledger['total_bits']
    root=Path(__file__).resolve().parents[1]
    hashes={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [root/'scripts'/'parameter_feasibility_checks.py',
                         root/'proofs'/'filtered_fourth_moment.md']}
    return dict(scope='Exact optimum within the stated finite parameter domain and arithmetic caps; no security certification',
        fixed_parameters=dict(q=Q,d=64,H=640,T=34,f='1/16',a='901/1024',
            gamma_squared_factor='21/2',kappa=24,outer_rank=16,r=list(SCHEDULE)),
        domain=dict(bases=[2,4,8,16,32,64,128,256],t1_offsets=[-1,0,1],t2_min=2,t2_max=19),
        radius_caps=dict(inner_weak=INNER_CAP,inner_gram=INNER_CAP,outer=OUTER_CAP),
        baseline_payload=baseline_ledger,best_payload=best_ledger,
        saved_bits=baseline_ledger['total_bits']-best_ledger['total_bits'],
        layers=list(best_path),search_history=history,source_hashes=hashes)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('work/joint_parameter_search.json'))
    args=parser.parse_args()
    result=run()
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(best_payload=result['best_payload'],saved_bits=result['saved_bits'])))
