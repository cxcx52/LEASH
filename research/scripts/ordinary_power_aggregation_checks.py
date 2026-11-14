"""Independent root-count toys and exact statistical/communication budgets.

Finite-field arithmetic only, with no protocol or solver implementation.
"""
from fractions import Fraction as F
from itertools import product
import json
from math import log2
from pathlib import Path


def small_scalar_field_checks():
    # F_9 = F_3[x]/(x^2+1); pair encoded as a+3b.
    def add(u,v):return (u%3+v%3)%3+3*((u//3+v//3)%3)
    def mul(u,v):
        a,b,c,d=u%3,u//3,v%3,v//3
        return (a*c+2*b*d)%3+3*((a*d+b*c)%3)
    assert all(any(mul(u,v)==1 for v in range(1,9)) for u in range(1,9))
    count=0
    for length in range(1,6):
        for coeffs in product(range(3),repeat=length):
            if not any(coeffs):continue
            degree=max(i for i,c in enumerate(coeffs) if c)
            roots=0
            for point in range(9):
                powers=[1]
                for unused in range(1,length):powers.append(mul(powers[-1],point))
                evaluated=0
                for coefficient,power in zip(coeffs,powers):
                    evaluated=add(evaluated,mul(coefficient,power))
                rows=[sum(c*(p%3 if coordinate==0 else p//3)
                          for c,p in zip(coeffs,powers))%3 for coordinate in range(2)]
                assert (evaluated==0)==(rows==[0,0])
                roots+=evaluated==0
            assert roots<=degree
            count+=1
    return count


def small_crt_checks():
    # R=F_5 x F_5: some coefficients can be nonzero zero divisors.
    count=0
    for length in range(1,4):
        for coeffs in product(range(25),repeat=length):
            if not any(coeffs):continue
            components=[[c%5 for c in coeffs],[c//5 for c in coeffs]]
            selected=next(v for v in components if any(v))
            degree=max(i for i,c in enumerate(selected) if c)
            root_counts=[]
            for component in components:
                root_counts.append(sum(sum(c*pow(point,i,5) for i,c in enumerate(component))%5==0
                                       for point in range(5)))
            assert root_counts[0]*root_counts[1]<=5*degree
            count+=1
    return count


def budgets():
    root=Path(__file__).resolve().parents[1]
    native=json.loads((root/'work'/'binary_frontend_arithmetic.json').read_text())['arithmetic']
    energy=json.loads((root/'work'/'joint_energy_parameter_search.json').read_text())
    q,d=4294967197,64
    count_lower=energy['challenge_certificate']['cardinality_lower_bound']
    schedule=[112,33,15,8,7,5,4]
    ordinary_common=F(sum(r+2 for r in schedule),count_lower)+F(7,2**164)
    result=[]
    for source_rows in (160,187):
        source_scalar_rows=2**27+4+1+source_rows+1
        lengths=[source_scalar_rows+1024]+[1024]*6
        k_values=[6+96]+[24+3+2*9]*6
        degrees_scalar=sum(m-1 for m in lengths)
        degrees_ring=sum(k+5 for k in k_values)
        assert degrees_ring==407
        assert degrees_scalar==134225055+(source_rows-160)
        scalar_error=F(degrees_scalar,q**6)
        ring_error=F(degrees_ring,q**32)
        source_error=F(1,2**160) if source_rows==160 else F(3*2**25-1,2**187)
        total=128*(ordinary_common+scalar_error+ring_error+source_error)
        assert total<F(1,2**128)
        original=F(energy['challenge_certificate']['full_Q128_statistical_bound'])
        wire=native['core_verifier_explicit_challenge_ledger']['totals']
        core_wire=wire['projection_two_bit_wire_bits']+wire['final_fold_challenge_three_bit_coordinate_wire_bits']+7*(6+d)*32
        source_wire=160*3*2**25 if source_rows==160 else 187
        result.append(dict(source_aggregation_rows=source_rows,
            scalar_lengths=lengths,ring_constraint_counts=k_values,
            scalar_degree_sum=degrees_scalar,ring_degree_sum=degrees_ring,
            scalar_aggregation_error=str(scalar_error),ring_aggregation_error=str(ring_error),
            source_aggregation_error=str(source_error),Q128_total_statistical_bound=str(total),
            Q128_total_statistical_bits=-log2(float(total)),
            Q128_margin_over_128_bits=-log2(float(total))-128,
            Q128_statistical_below_2_minus_128=True,
            increase_over_old_independent160_budget=str(total-original),
            seven_layer_scalar_challenge_bits=7*6*32,
            seven_layer_ring_challenge_bits=7*d*32,
            core_explicit_verifier_bits=core_wire,
            source_plus_core_explicit_verifier_raw_bits=core_wire+source_wire,
            source_plus_core_explicit_verifier_GiB=float(F(core_wire+source_wire,8*2**30)),
            prover_payload_changed_by_core_aggregation=False))
    return result


if __name__=='__main__':
    result=dict(scope='Independent finite root-count checks and exact rational budgets only',
        scalar_field_nonzero_polynomials=small_scalar_field_checks(),
        CRT_nonzero_polynomial_cases=small_crt_checks(),profiles=budgets())
    out=Path(__file__).resolve().parents[1]/'work'/'ordinary_power_aggregation_checks.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(scalar_cases=result['scalar_field_nonzero_polynomials'],
        CRT_cases=result['CRT_nonzero_polynomial_cases'],
        profiles=[{k:p[k] for k in ('source_aggregation_rows','scalar_degree_sum',
          'ring_degree_sum','Q128_total_statistical_bits','source_plus_core_explicit_verifier_GiB')}
          for p in result['profiles']]),indent=2))
