"""Independent exact probability examples for weighted modal-loss refinement.

Finite probability tables only: no cryptographic transcript, prover, collision
solver, or security experiment implementation is supplied.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import product
import json


def modal_error_collision(masses):
    total=sum(masses.values(),F(0))
    if not masses:
        return None,F(0),F(0)
    mode=min(masses,key=lambda value:(-masses[value],value))
    error=total-masses[mode]
    collision=total*total-sum((p*p for p in masses.values()),F(0))
    assert error*error<=total*error<=collision
    return mode,error,collision


def exact_game():
    """One common extended anchor law; fresh randomized final replies.

    Labels N/G designate disjoint analysis subsets. This table checks modal
    probability algebra, not the protocol-specific polynomial-root containment.
    """
    r=3
    challenges=(-1,0,1)
    theta_weights=(F(1,3),F(2,3))
    # Anchor labels: 0=bottom, 1=Bad_N, 2=Bad_G, 3=other completed.
    conditional_anchor=((F(1,2),F(1,4),F(1,8),F(1,8)),
                        (F(1,4),F(1,8),F(1,4),F(3,8)))
    eta_h=eta_y=eta_g=F(0)
    bad_n=bad_g=F(0)
    weighted_h=weighted_selected_y=weighted_g=F(0)
    selected_indicator_mass=selected_collision_mass=F(0)
    selected_indices=set()

    def branch(theta,upper,cs,coin):
        accepted=(sum(c*c for c in cs)+2*upper+theta+coin)%5!=0
        first_opening=(sum(cs)+upper+coin)%2
        h=[0]*r
        if (upper+theta)%4:
            h[(upper+theta)%r]=1
        if (sum(cs)+coin)%4==0:
            h[(upper+1)%r]+=1
        z=sum((i+2)*c for i,c in enumerate(cs))+coin*(upper+1)+(cs[0]*cs[1])%3
        return accepted,first_opening,tuple(h),z

    for theta,theta_weight in enumerate(theta_weights):
        assert sum(conditional_anchor[theta])==1
        for anchor,anchor_probability in enumerate(conditional_anchor[theta]):
            weight=theta_weight*anchor_probability
            if anchor==0:
                continue
            if anchor==1:bad_n+=weight
            if anchor==2:bad_g+=weight
            source=[anchor+i for i in range(r)]
            for upper in range(3):
                prefix_weight=weight/3
                h_masses=defaultdict(F)
                for cs in product(challenges,repeat=r):
                    for coin in (0,1):
                        accepted,opening,h,z=branch(theta,upper,cs,coin)
                        if accepted and opening==anchor%2:
                            h_masses[h]+=F(1,2*3**r)
                h_mode,e_h,c_h=modal_error_collision(h_masses)
                eta_h+=prefix_weight*c_h
                if anchor==1:weighted_h+=prefix_weight*e_h
                selector=None if h_mode is None else next(
                    (index for index,value in enumerate(h_mode) if value!=0),None)
                # selector is fixed from anchor+upper before all final challenges.
                if selector is not None:selected_indices.add(selector)
                for index in range(r):
                    for complement in product(challenges,repeat=r-1):
                        y_masses=defaultdict(F)
                        for challenge in challenges:
                            cs=list(complement)
                            cs.insert(index,challenge)
                            for coin in (0,1):
                                accepted,opening,h,z=branch(theta,upper,cs,coin)
                                if accepted and opening==anchor%2:
                                    y_masses[z-challenge*source[index]]+=F(1,6)
                        unused,e_y,c_y=modal_error_collision(y_masses)
                        slice_weight=prefix_weight/F(r*3**(r-1))
                        eta_y+=slice_weight*c_y
                        if anchor==1 and index==selector:
                            selected_indicator_mass+=slice_weight
                            selected_collision_mass+=slice_weight*c_y
                            weighted_selected_y+=r*slice_weight*e_y
                if anchor==2:
                    # The selected pair depends only on the completed anchor.
                    pair=(0,2)
                    for remaining in challenges:
                        g_masses=defaultdict(F)
                        for c0,c2,coin in product(challenges,challenges,(0,1)):
                            cs=(c0,remaining,c2)
                            accepted,opening,h,z=branch(theta,upper,cs,coin)
                            if accepted and opening==anchor%2:
                                y=z-sum(cs[i]*source[i] for i in pair)
                                g_masses[y]+=F(1,18)
                        unused,e_g,c_g=modal_error_collision(g_masses)
                        eta_g+=prefix_weight*c_g/3
                        weighted_g+=prefix_weight*e_g/3
    assert selected_indices=={0,1,2}
    assert selected_indicator_mass<=bad_n/r
    assert selected_collision_mass<=eta_y
    assert weighted_h**2<=bad_n*eta_h
    assert weighted_selected_y**2<=r*bad_n*eta_y
    assert weighted_g**2<=bad_g*eta_g
    bad=bad_n+bad_g
    combined=weighted_h+weighted_selected_y+weighted_g
    coefficient=2*eta_h+2*r*eta_y+eta_g
    assert combined**2<=bad*coefficient
    return {key:str(value) for key,value in dict(
        bad_n=bad_n,bad_g=bad_g,eta_h=eta_h,eta_y=eta_y,eta_g=eta_g,
        weighted_h=weighted_h,weighted_selected_y=weighted_selected_y,
        weighted_g=weighted_g,selector_event_mass=selected_indicator_mass,
        selector_event_bound=bad_n/r,combined_mass=combined,
        combined_squared_bound=bad*coefficient).items()}


def scalar_bound_checks():
    count=0
    for kappa,s,t in product((F(0),F(1,16),F(1,4)),
                            (F(0),F(1,32),F(1,8),F(1,4)),
                            (F(0),F(1,32),F(1,16),F(1,8),F(1,4))):
        # eta0=s^2 and K^2=t^3, so the asserted bound is rational kappa+s+t.
        for numerator in range(65):
            bad=F(numerator,64)
            remainder=bad*bad-kappa*bad-s*s
            premise=(remainder<=0 or remainder*remainder<=t**3*bad)
            if premise:assert bad<=kappa+s+t
            count+=1
    return count


def canonical_checks():
    count=0
    for x in range(9):
        for y in range(9-x):
            for z in range(9-x-y):
                modal_error_collision({i:F(n,8) for i,n in enumerate((x,y,z)) if n})
                count+=1
    return count


def selector_scale_checks():
    """The sqrt(r) scale is needed by uniform-coordinate information alone."""
    rows=[]
    for r,bad,accepted,modes in product((2,3,7), (F(1,7),F(2,3)),
                                      (F(1,4),F(3,4)), (2,5,17)):
        # Exactly one index has a nontrivial modal distribution on bad anchors.
        # All other cases have zero errors/collisions, and the index is fixed
        # before the independently uniform coordinate choice.
        unused,error,collision=modal_error_collision(
            {i:accepted/modes for i in range(modes)})
        eta_y=bad*collision/r
        selected_error=bad*error
        ratio=selected_error**2/(r*bad*eta_y)
        assert ratio==F(modes-1,modes)
        assert (selected_error**2>bad*eta_y)==(r*(modes-1)>modes)
        rows.append((r,str(bad),modes,str(ratio)))
    return len(rows)


def forbidden_conditioning_controls():
    # A nongated successful-search anchor can have b_theta > epsilon_theta.
    bad,epsilon=F(1),F(1,4)
    assert bad*epsilon<bad*bad
    # If the analysis selector were allowed to see I, it could always choose I.
    # The mass bound used by SELECT would then be false.
    r=3
    bad=F(1,2)
    actual_indicator_mass=sum((bad/r for index in range(r)),F(0))
    assert actual_indicator_mass==bad>bad/r
    return 2


if __name__=='__main__':
    print(json.dumps(dict(scope='Exact probability identities only; not a cryptographic simulation',
        canonical_subprobability_tables=canonical_checks(),
        scalar_implication_cases=scalar_bound_checks(),
        selector_scale_cases=selector_scale_checks(),
        forbidden_conditioning_negative_controls=forbidden_conditioning_controls(),
        weighted_game=exact_game()),indent=2))
