"""Exact arithmetic screening of repaired ordinary-core parameters.

This is a norm/cost certificate, not a lattice hardness estimator or prover.
All decisive norm comparisons use integers or Fraction.
"""
from fractions import Fraction as F
from math import isqrt, log2
import json

from certified_filtered_challenges_checks import (certified_count_lower,
    tail_certificate, unit_cube_parameter_certificate)


def ceil_sqrt(value):
    value = F(value)
    root = isqrt(value.numerator // value.denominator)
    return root + (root*root < value)


def digits_for(value, base):
    count, power = 0, 1
    while power < value:
        count += 1
        power *= base
    return max(2, count)


def cube_operator_upper(degree):
    # sin(pi/(2d)) > x-x^3/6 at x=157/(100d), using pi>157/50.
    x = F(157, 100*degree)
    return F(2)/(x-x**3/6)


def carry_bound(base, digits):
    return F(base, 2*(base-1))*(1-F(1, base**(digits-1)))


def core_cap(q, degree, rank_n, multiplicity_r, kappa, beta,
             base, t1, t2, operator_bound=31, recursive=True,
             fold_second_moment_factor=F(32, 9),fold_failure=F(1,4),
             honest_threshold=552,gamma_squared_factor=None):
    """Deterministic target cap on a fold event of probability >1-fold_failure.

    The covariance factor and honest JL threshold are explicit inputs.
    Markov sets Gamma^2=factor*d*beta^2/fold_failure. Upper triangles are packed.
    """
    beta_squared = F(beta)**2
    pairs = multiplicity_r*(multiplicity_r+1)//2
    z_count = rank_n*degree
    uniform_count = degree*(multiplicity_r*kappa+pairs)  # t and h
    garbage_count = degree*pairs
    assert 0<fold_failure<1 and honest_threshold>512
    slack_squared=F(honest_threshold,120)
    # An override needs its own concentration proof; the default is Markov.
    gamma_factor=(fold_second_moment_factor/fold_failure if gamma_squared_factor is None
                  else F(gamma_squared_factor))
    assert gamma_factor>0
    gamma = ceil_sqrt(gamma_factor*degree*beta_squared)
    z_squared = F(z_count*base*base, 4)
    z_squared += (F(gamma, base)+F(ceil_sqrt(z_count), 2))**2
    uniform_squared = uniform_count*(F((t1-1)*base*base, 4)
        +(F(q, 2*base**(t1-1))+carry_bound(base,t1))**2)
    # ||packed g|| <= sqrt(d)*beta^2, before coefficientwise centering.
    garbage_norm = ceil_sqrt(degree*beta_squared**2)
    garbage_squared = F(garbage_count*(t2-1)*base*base, 4)
    garbage_squared += (F(garbage_norm, base**(t2-1))
        +ceil_sqrt(garbage_count)*carry_bound(base,t2))**2
    target_beta = ceil_sqrt(z_squared+uniform_squared+garbage_squared)
    actual_B = ceil_sqrt(slack_squared*target_beta**2) if recursive else target_beta
    source_slack_beta = ceil_sqrt(slack_squared*beta_squared)
    outer_msis = 2*actual_B
    inner_weak_msis = 8*operator_bound*(base+1)*actual_B
    inner_gram_msis = 2*(base+1)*actual_B+4*operator_bound*source_slack_beta
    next_length = (2*rank_n + multiplicity_r*t1*kappa+(t1+t2)*pairs)
    jl_ok = 250**2*slack_squared*beta_squared <= q*q
    return {
        "d": degree, "n": rank_n, "r": multiplicity_r, "kappa": kappa,
        "beta": beta, "b": base, "t1": t1, "t2": t2,
        "honest_threshold": honest_threshold,
        "gamma_ceiling": gamma, "target_beta": target_beta,
        "actual_B": actual_B, "recursive_B": recursive,
        "input_ring_length": rank_n*multiplicity_r,
        "next_ring_length": next_length,
        "auxiliary_ring_length": next_length-2*rank_n,
        "outer_msis_bound": outer_msis,
        "inner_weak_msis_bound": inner_weak_msis,
        "inner_gram_msis_bound": inner_gram_msis,
        "standard_integer_msis_nontrivial": max(outer_msis,inner_weak_msis,inner_gram_msis)<q,
        "jl_modulus_condition": jl_ok,
    }


def signed_bits(absolute_bound):
    """Fixed-width index in [-floor(bound),floor(bound)]."""
    bound=F(absolute_bound)
    bound=bound.numerator//bound.denominator
    return (2*bound).bit_length()


def transcript_ledger(rows,q=4294967197,outer_rank=16,aggregation=6):
    """Conservative fixed-width prover payload, ordinary final level.

    Omits public statements, verifier challenges, Fiat--Shamir material, and
    framing. Includes two outer commitments even on the ordinary final level.
    This is a possible encoding upper bound, not an optimized size estimate.
    """
    qbits=(q-1).bit_length()
    round_bits=0
    for row in rows:
        d=row['d']
        round_bits += 2*outer_rank*d*qbits
        round_bits += 1024*signed_bits(ceil_sqrt(row['honest_threshold']*row['beta']**2))
        round_bits += aggregation*d*qbits
    last=rows[-1]
    d,n,r,b=last['d'],last['n'],last['r'],last['b']
    t1,t2=last['t1'],last['t2']
    pairs=r*(r+1)//2
    zcount=n*d
    ucount=d*(r*last['kappa']+pairs)
    gcount=d*pairs
    digit_bits=(b-1).bit_length() # b consecutive centered digits, b a power of 2
    zbits=zcount*(digit_bits+signed_bits(F(last['gamma_ceiling'],b)+F(1,2)))
    ubits=ucount*((t1-1)*digit_bits+signed_bits(F(q,2*b**(t1-1))+carry_bound(b,t1)))
    ghigh=min(F(last['beta']**2),F(q,2))/b**(t2-1)+carry_bound(b,t2)
    gbits=gcount*((t2-1)*digit_bits+signed_bits(ghigh))
    return dict(round_bits=round_bits,final_bits=zbits+ubits+gbits,
                total_bits=round_bits+zbits+ubits+gbits,
                total_KiB=(round_bits+zbits+ubits+gbits)/8192)


def extraction_ledger():
    r_values=[112,33,15,8,7,5,4]
    count=certified_count_lower(64,31,7,16)
    calls=F(1)
    for r in r_values:
        calls*=1+F(r*count,count-1)
    probability=F(sum(r+2 for r in r_values),count)
    q=4294967197
    total=probability+F(7,2**164)+F(7,q**6)+F(7,q**32)
    assert 132779520<calls<132779521
    assert probability<F(1,2**140)
    assert total+F(1,2**160)<F(1,2**140)
    honest_one=F(67,132)
    return dict(challenge_count_lower=count,calls_floor=calls.numerator//calls.denominator,
                calls_log2=log2(calls),challenge_error_bits=-log2(probability),
                ordinary_total_error_bits=-log2(total),
                honest_seven_layer_lower=float(honest_one**7),
                independent_full_attempt_expected_upper=float((1/honest_one)**7))


def affine_toy():
    q,d,r,n,beta=4294967197,64,32,4096,2048
    packed_ring_length=r*n
    assert beta**2==packed_ring_length*d//2
    relaxed_squared=F(23,5)*beta**2
    # sqrt(Md/2)*sqrt(relaxed_squared)+relaxed_squared/2 < q/2.
    remaining=F(q,2)-relaxed_squared/2
    assert remaining>0 and F(packed_ring_length*d,2)*relaxed_squared<remaining**2
    source_modulus=2**d+1
    smallest_prime=274177
    assert source_modulus%smallest_prime==0
    assert all(source_modulus%v for v in range(3,smallest_prime,2))
    assert F(2,smallest_prime**9)<F(1,2**160)
    # 10000 constraints, 11072 variables, nine affine aggregations.
    assert 11072+(3+9)*10000==packed_ring_length
    options=[]
    for b in (2,4,8,16,32,64,128,256):
        for t2 in range(2,20):
            row=core_cap(q,d,n,r,16,beta,b,digits_for(q,b),t2)
            if row['standard_integer_msis_nontrivial'] and row['jl_modulus_condition']:
                options.append(row)
    result=min(options,key=lambda x:(x['target_beta'],x['next_ring_length']))
    result.update(affine_packed_ring_length=packed_ring_length,affine_repetitions=9,
                  smallest_source_prime=smallest_prime,lifting_verified=True)
    return result


def check_caps():
    assert unit_cube_parameter_certificate(64,4294967197)
    for b in (2,4,8,16):
        for t in range(2,7):
            for original in range(-1000,1001):
                value=original
                for unused in range(t-1):
                    digit=(value+b//2)%b-b//2
                    assert abs(digit)<=F(b,2)
                    value=(value-digit)//b
                assert abs(value)<=F(abs(original),b**(t-1))+carry_bound(b,t)
    assert 44174**2+48411**2==4294967197
    assert F(23,5)*16384**2<4294967197
    assert 2*max(2**25,3*2**25)<4294967197


def certified_acceptance(degree, threshold, denominator=1024):
    if not tail_certificate(degree,threshold,denominator-1,denominator):
        return None
    lo,hi=1,denominator-1
    while lo<hi:
        mid=(lo+hi)//2
        if tail_certificate(degree,threshold,mid,denominator):
            hi=mid
        else:
            lo=mid+1
    return 1-F(lo,denominator)


def recursion_screen(q=4294967197, degree=64, kappa=16, operator_bound=31,
                     acceptance=F(9,16),fold_failure=F(1,4),honest_threshold=552,
                     gamma_squared_factor=None):
    schedule = [112,33,15,8,7,5,4]
    rank_n, beta = 37450, 16384
    rows = []
    for index,r in enumerate(schedule):
        n = rank_n
        candidates=[]
        for base in (2,4,8,16,32,64,128,256):
            t1=digits_for(q,base)
            for t2 in range(2,20):
                item=core_cap(q,degree,n,r,kappa,beta,base,t1,t2,
                              operator_bound=operator_bound,
                              recursive=index<len(schedule)-1,
                              fold_second_moment_factor=2/acceptance,
                              fold_failure=fold_failure,honest_threshold=honest_threshold,
                              gamma_squared_factor=gamma_squared_factor)
                if item["standard_integer_msis_nontrivial"] and item["jl_modulus_condition"]:
                    if index+1 < len(schedule):
                        next_r=schedule[index+1]
                        splits=[]
                        for nu in range(1,(next_r-1)//2+1):
                            mu=next_r-2*nu
                            next_n=max((n+nu-1)//nu,
                                (item["auxiliary_ring_length"]+mu-1)//mu)
                            splits.append((next_n,nu,mu))
                        next_n,nu,mu=min(splits)
                        item.update(next_n=next_n,next_r=next_r,nu=nu,mu=mu,
                                    next_padded_ring_length=next_n*next_r)
                    candidates.append(item)
        if not candidates:
            rows.append({"level":index+1,"no_feasible_candidate_in_search_grid":True,
                         "beta":beta,"ring_length":rank_n*r})
            break
        best=min(candidates,key=lambda item:(item["target_beta"],item["next_ring_length"]))
        best["level"]=index+1
        rows.append(best)
        rank_n,beta=best.get("next_n",0),best["target_beta"]
    return rows


if __name__ == "__main__":
    check_caps()
    comparisons=[]
    for threshold in range(28,41):
        acceptance=certified_acceptance(64,threshold)
        if acceptance is None:
            continue
        rows=recursion_screen(operator_bound=threshold,acceptance=acceptance)
        comparisons.append({"T":threshold,"acceptance_lower":str(acceptance),
                            "complete_grid_path":len(rows)==7 and "actual_B" in rows[-1],
                            "peak_inner_bound":max(row.get("inner_weak_msis_bound",0) for row in rows),
                            "final_target_beta":rows[-1].get("target_beta"),
                            "payload_KiB":transcript_ledger(rows)['total_KiB'] if 'actual_B' in rows[-1] else None})
    screen=recursion_screen(operator_bound=34,acceptance=certified_acceptance(64,34))
    high_complete=recursion_screen(operator_bound=34,acceptance=F(901,1024),
                                  honest_threshold=640,fold_failure=F(1,16))
    honest_layer=1-F(512,512+(640-512)**2)-F(1,16)
    assert honest_layer==F(479,528) and 2*honest_layer**7>1
    assert F(640,120)*16384**2<4294967197
    for row in screen+high_complete:
        assert row['standard_integer_msis_nontrivial'] and row['jl_modulus_condition']
        if 'next_n' in row:
            assert row['next_r']==2*row['nu']+row['mu']
            assert row['next_n']*row['nu']>=row['n']
            assert row['next_n']*row['mu']>=row['auxiliary_ring_length']
    result={"screen_T34":screen,"T_comparisons":comparisons,
            "extraction":extraction_ledger(),"affine_toy":affine_toy(),
            "ordinary_payload_T34":transcript_ledger(screen),
            "high_completeness_screen":high_complete,
            "high_completeness_seven_layer_lower":float(honest_layer**7),
            "high_completeness_payload":transcript_ledger(high_complete)}
    print(json.dumps(result,indent=2))
