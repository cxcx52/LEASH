"""Fixed-path outer-rank cost/communication screen, with pinned Sage models.

No lattice instances, lattice reduction, solver, prover, or transcripts. The two
exact arithmetic paths remain fixed; only both outer commitment row ranks vary.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from computational_parameter_screen import PIN,Q,optimum_dimension,crt_candidate
from joint_parameter_search import verify_path
from joint_energy_parameter_search import verify_saved_result
from parameter_feasibility_checks import transcript_ledger


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--estimator',type=Path,
        required=True, help='Clean external estimator checkout at the pinned commit')
    parser.add_argument('--output',type=Path,default=Path('work/outer_rank_parameter_screen.json'))
    args=parser.parse_args()
    research=Path(__file__).resolve().parents[1]
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

    def costs(rows,columns,radius,dimension=None):
        assert rows<columns and 1<radius<Q
        dim=dimension or optimum_dimension(rows,columns,radius)
        params=SIS.Parameters(n=rows,m=columns,q=Q,length_bound=radius,norm=2)
        output={}
        for name,model in models.items():
            cost=SISLattice.cost_euclidean(params,d=dim,red_cost_model=model)
            output[name]=None if cost['rop']==oo else float(log(cost['rop'],2))
        block=int(cost['beta'])
        return dict(n=rows,m=columns,dimension=dim,block_size=block,
            delta=float(cost['delta']),log2_cost=output,
            matzov_within_documented_fit=block<=1024)

    def screen(level,role,rank,columns,radius):
        n,m=64*rank,64*columns
        generic=costs(n,m,ZZ(radius))
        energy=radius*radius//Q
        candidate=crt_candidate(n//2,m,energy)
        if candidate is None:
            crt=dict(reduced_energy=energy,n=n//2,m=m,
                status='no GSA fit through min(m,65536)' if energy
                       else 'zero reduced energy: no nonzero integer vector')
        else:
            dim,block=candidate
            crt=costs(n//2,m,sqrt(ZZ(energy)),dim)
            crt['reduced_energy']=energy
            assert crt['block_size']==block
        return dict(level=level,role=role,ring_rows=rank,ring_columns=columns,
            radius=radius,generic=generic,single_crt=crt)

    def minima(screens):
        result={}
        for name in models:
            candidates=[]
            for row in screens:
                for route in ('generic','single_crt'):
                    item=row[route]
                    value=item.get('log2_cost',{}).get(name)
                    if value is not None:
                        candidates.append((value,row['level'],row['role'],route,
                                           item['block_size'],item['matzov_within_documented_fit']))
            value,level,role,route,block,fit=min(candidates)
            result[name]=dict(log2_cost=value,level=level,role=role,route=route,
                block_size=block,matzov_within_documented_fit=fit)
        return result

    inputs={
        'cube':('joint_parameter_search.json','joint_parameter_model_screen.json'),
        'energy_ball':('joint_energy_parameter_search.json','joint_energy_model_screen.json')}
    loaded={}
    for name,(path_name,model_name) in inputs.items():
        path_file,model_file=research/'work'/path_name,research/'work'/model_name
        saved=json.loads(path_file.read_text(encoding='utf-8'))
        prior=json.loads(model_file.read_text(encoding='utf-8'))
        if name=='cube':verify_path(saved['layers'])
        else:verify_saved_result(saved)
        assert saved['fixed_parameters']['outer_rank']==16
        assert prior['estimator_commit']==PIN
        assert prior['path_input_sha256']==digest(path_file)
        assert prior['profiles'][0]['layers']==saved['layers']
        assert transcript_ledger(saved['layers'],outer_rank=16)==prior['profiles'][0]['payload']
        loaded[name]=(saved,prior,path_file,model_file)
    baseline=minima(loaded['cube'][1]['profiles'][0]['screens'])
    result=[]
    for name,(saved,prior,path_file,model_file) in loaded.items():
        path=saved['layers']
        inner=[row for row in prior['profiles'][0]['screens'] if row['role']=='inner']
        assert len(inner)==7
        old_payload=transcript_ledger(path,outer_rank=16)
        ranks=[]
        for rank in range(4,17):
            outer=[]
            for row in path:
                pairs=row['r']*(row['r']+1)//2
                outer.append(screen(row['level'],'outer_first',rank,
                    row['r']*row['t1']*24+pairs*row['t2'],row['outer_msis_bound']))
                outer.append(screen(row['level'],'outer_second',rank,
                    pairs*row['t1'],row['outer_msis_bound']))
            outer_min=minima(outer)
            core_min=minima(inner+outer)
            preserves={model:core_min[model]['log2_cost']>=baseline[model]['log2_cost']
                       for model in models}
            payload=transcript_ledger(path,outer_rank=rank)
            savings=old_payload['total_bits']-payload['total_bits']
            assert savings==7*2*(16-rank)*64*32
            assert payload['final_bits']==old_payload['final_bits']
            if rank==16:
                old_outer=[row for row in prior['profiles'][0]['screens'] if row['role']!='inner']
                for old,new in zip(old_outer,outer):
                    assert (old['level'],old['role'],old['radius'])==(new['level'],new['role'],new['radius'])
                    for route in ('generic','single_crt'):
                        for model,value in new[route].get('log2_cost',{}).items():
                            assert value==old[route]['log2_cost'][model]
            entry=dict(outer_rank=rank,payload=payload,saved_bits_from_same_path_outer16=savings,
                ring_equations_in_each_target=24+3+2*rank,
                outer_model_minima=outer_min,core_model_minima=core_min,
                preserves_cube_baseline_by_model=preserves,
                preserves_all_five_cube_baselines=all(preserves.values()),screens=outer)
            ranks.append(entry)
            print(json.dumps(dict(profile=name,rank=rank,KiB=payload['total_KiB'],
                passes=entry['preserves_all_five_cube_baselines'],
                outer_min={k:v['log2_cost'] for k,v in outer_min.items()})),flush=True)
        passing=[row for row in ranks if row['preserves_all_five_cube_baselines']]
        assert passing
        selected=min(passing,key=lambda row:row['outer_rank'])
        result.append(dict(profile=name,fixed_parameters=saved['fixed_parameters'],
            path_file=str(path_file.relative_to(research)),path_sha256=digest(path_file),
            original_model_file=str(model_file.relative_to(research)),original_model_sha256=digest(model_file),
            path=path,inner_screens_unchanged=inner,original_payload=old_payload,
            minimum_passing_outer_rank=selected['outer_rank'],
            selected_parameters={**saved['fixed_parameters'],'outer_rank':selected['outer_rank']},
            selected_payload=selected['payload'],
            selected_target_full_ring_equations=selected['ring_equations_in_each_target'],
            requires_fresh_rank_specific_CRS_and_target_relations=True,ranks=ranks))
    output=dict(scope='Fixed exact arithmetic paths; pure heuristic cost/communication screening; no security certification',
        estimator_commit=revision,sage_version=version,norm='coefficient Euclidean standard nonzero integer SIS',
        q=Q,d=64,outer_rank_domain=list(range(4,17)),inner_rank=24,
        threshold_rule='Use unrounded pinned cube path minimum separately for each model',
        baseline_cube_minima=baseline,profiles=result)
    args.output.write_text(json.dumps(output,indent=2,allow_nan=False)+'\n',encoding='utf-8')


if __name__=='__main__':main()
