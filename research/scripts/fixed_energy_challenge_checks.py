"""Exact cardinality/tail/moment certificates for bounded-energy challenges.

Pure counting and probability arithmetic. No cryptographic prover, RNG,
commitment, protocol transcript, or lattice algorithm is implemented.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import factorial, log2
import json

from certified_filtered_challenges_checks import certified_op_below


D = 64
ANGLES = ((8,F(1707,2000)), (12,F(933,1000)), (16,F(9619,10000)))
TILTS = (F(2,3),F(3,4),F(4,5),F(5,6),F(6,7),F(7,8),F(9,10),F(19,20),F(1))


@lru_cache(None)
def energy_counts(d):
    if d == 0:
        return (1,)
    previous = energy_counts(d-1)
    out = [0]*(4*d+1)
    for e,count in enumerate(previous):
        out[e] += count
        out[e+1] += 2*count
        out[e+4] += 2*count
    return tuple(out)


@lru_cache(None)
def ball_count(d, budget):
    return sum(energy_counts(d)[:budget+1]) if budget >= 0 else 0


def shell_count(d, energy):
    return energy_counts(d)[energy] if 0 <= energy <= 4*d else 0


def ball_unrank(d, budget, rank):
    """Lexicographic integer-rank decoder for the exact uniform finite ball.

    A uniform integer rank would induce a uniform ball element. No random
    sampling is implemented here.
    """
    assert 0 <= rank < ball_count(d,budget)
    result = []
    for remaining in range(d-1,-1,-1):
        for symbol in (-2,-1,0,1,2):
            count = ball_count(remaining,budget-symbol*symbol)
            if rank < count:
                result.append(symbol)
                budget -= symbol*symbol
                break
            rank -= count
        else:
            raise AssertionError("Unranking range error")
    assert rank == 0
    return tuple(result)


def ball_rank(vector, budget):
    rank = 0
    for position, actual in enumerate(vector):
        assert actual in (-2,-1,0,1,2)
        remaining = len(vector)-position-1
        rank += sum(ball_count(remaining,budget-symbol*symbol)
                    for symbol in (-2,-1,0,1,2) if symbol < actual)
        budget -= actual*actual
    assert budget >= 0
    return rank


def exp_lower(x, terms=80):
    """Strict rational lower bound on exp(x), for positive rational x."""
    assert x > 0
    term = total = F(1)
    for k in range(1,terms+1):
        term *= x/k
        total += term
    return total


def tilted_mgf_certificate(t):
    assert 0 < t <= 1
    z = 1+2*t+2*t**4
    variance = (2*t+8*t**4)/z
    fourth = (2*t+32*t**4)/z
    # k=1 exact; k=2 checked; subsequent moment ratios <4 while
    # Gaussian comparison ratios >=5*variance>4.
    assert fourth <= 3*variance*variance
    assert 5*variance > 4
    return z,variance,fourth


@lru_cache(None)
def tilted_operator_tail(t, threshold, directions, cosine_squared_lower):
    z,variance,_ = tilted_mgf_certificate(t)
    exponent = cosine_squared_lower*threshold*threshold/(D*variance)
    return F(D*directions,2)/exp_lower(exponent)


def ball_bad_bound(energy, t, threshold, directions, cosine_squared_lower):
    z,_,_ = tilted_mgf_certificate(t)
    multiplier = z**D/(t**energy*ball_count(D,energy))
    return multiplier*tilted_operator_tail(t,threshold,directions,cosine_squared_lower)


def retained_count_lower(count,bad_upper):
    assert 0 <= bad_upper < 1
    lower = count*(1-bad_upper)
    # The analytic tail is STRICTLY below the rational bound.
    return lower.numerator//lower.denominator+1


def raw_ball_moments(energy):
    counts = energy_counts(D)
    total = ball_count(D,energy)
    mean_energy = F(sum(e*counts[e] for e in range(energy+1)),total)
    second_energy = F(sum(e*e*counts[e] for e in range(energy+1)),total)
    m2 = mean_energy/D
    m4 = F(2*ball_count(D-1,energy-1)+32*ball_count(D-1,energy-4),total)
    m22 = (second_energy-D*m4)/(D*(D-1))
    g = 2*m22-m2*m2+(m4-3*m22)/D
    variance_energy = second_energy-mean_energy*mean_energy
    return {"v0":m2,"m4":m4,"m22":m22,"g0":g,"energy_variance":variance_energy}


def bits_bound(probability):
    assert 0 < probability <= 1
    return (probability.denominator//probability.numerator).bit_length()-1


def small_general_moment_checks():
    """Independent direct enumeration of the non-iid raw-ball moment lemma."""
    reports = []
    for d,budget,threshold in ((2,3,2),(4,5,2)):
        raw = tuple(c for c in product((-2,-1,0,1,2),repeat=d) if sum(x*x for x in c)<=budget)
        selected = tuple(c for c in raw if certified_op_below(c,threshold))
        p = F(len(selected),len(raw))
        v0 = F(sum(c[0]**2 for c in raw),len(raw))
        m4 = F(sum(c[0]**4 for c in raw),len(raw))
        m22 = F(sum(c[0]**2*c[1]**2 for c in raw),len(raw))
        v = F(sum(c[0]**2 for c in selected),len(selected))
        assert all(F(sum(c[i]*c[j] for c in selected),len(selected)) == (v if i==j else 0)
                   for i in range(d) for j in range(d))
        energy_variance = F(sum((sum(x*x for x in c)-d*v0)**2 for c in raw),len(raw))
        assert energy_variance == d*m4+d*(d-1)*m22-d*d*v0*v0
        g = 2*m22-v0*v0+(m4-3*m22)/d
        assert g == energy_variance/(d*d)+(1-F(2,d))*m22 >= 0
        assert (v-v0)**2 <= energy_variance*(1-p)/(p*d*d)
        sources = (tuple(range(1,d+1)), tuple((-1)**j for j in range(d)))
        def image(c):
            out = []
            for source in sources:
                row = [0]*d
                for i,x in enumerate(source):
                    for j,y in enumerate(c):
                        row[(i+j)%d] += x*y*(1 if i+j<d else -1)
                out.extend(row)
            return tuple(out)
        columns = [image(tuple(int(i==j) for i in range(d))) for j in range(d)]
        gram = [[sum(x*y for x,y in zip(a,b)) for b in columns] for a in columns]
        t = sum(x*x for source in sources for x in source)
        assert all(gram[i][i] == t for i in range(d))
        trace_square = sum(x*x for row in gram for x in row)
        raw_values = [sum(x*x for x in image(c)) for c in raw]
        raw_fourth = F(sum(x*x for x in raw_values),len(raw))
        assert raw_fourth == m22*((d*t)**2+2*trace_square)+(m4-3*m22)*d*t*t
        assert raw_fourth-(v0*d*t)**2 <= g*d*d*t*t
        selected_values = [sum(x*x for x in image(c)) for c in selected]
        selected_variance = F(sum((x-v*d*t)**2 for x in selected_values),len(selected))
        assert selected_variance <= (g/p-(v-v0)**2)*d*d*t*t
        reports.append({"d":d,"raw_energy_cap":budget,"operator_threshold":threshold,
                        "raw_count":len(raw),"selected_count":len(selected),
                        "v0":str(v0),"selected_v":str(v),"g":str(g),
                        "selected_variance":str(selected_variance)})
    return reports


def main():
    # All trigonometric constants used in the angle nets have exact proofs.
    assert F(707,500)**2 < 2
    assert (2+F(707,500))/4 == F(1707,2000)
    assert F(433,250)**2 < 3
    assert (2+F(433,250))/4 == F(933,1000)
    assert F(4619,5000)**2 < F(1707,2000)
    assert (1+F(4619,5000))/2 == F(9619,10000)
    for t in TILTS:
        tilted_mgf_certificate(t)

    count71 = sum(factorial(D)//(factorial(j)*factorial(71-4*j)*factorial(3*j-7))
                  *2**(71-3*j) for j in range(3,18))
    assert count71 == shell_count(D,71)
    assert count71 == 914575309776010636758020194460195880960
    assert count71 < 3*2**128  # (r+2)/N cannot reach 2^-128 for any r>=1.
    tilt71 = F(2,3)
    z71,var71,_ = tilted_mgf_certificate(tilt71)
    shell_probability = count71*tilt71**71/z71**D
    assert var71 == F(236,221)
    assert shell_probability == F(count71*3**185*2**71,221**64)
    shell_rows = []
    for threshold in (15,26,27,28,30,31):
        choices = [(tilted_operator_tail(tilt71,threshold,m,c)/shell_probability,m)
                   for m,c in ANGLES]
        bad,directions = min(choices)
        shell_rows.append({"T":threshold,"directions":directions,
                           "rational_bad_bound_display":float(bad),
                           "certifies_positive_count":bad<1,
                           "count_lower":retained_count_lower(count71,bad) if bad<1 else None})
        if threshold == 27:
            assert bad < F(1,2)
        if threshold == 15:
            assert bad > 1  # Only this certificate fails; no nonexistence claim.

    # A bounded, explicitly reported exploration grid, no unbounded optimizer.
    grid = []
    for energy in (96,100,104,108,112,116,120,128,144,256):
        for threshold in (29,30,31,32,34):
            choices = [(ball_bad_bound(energy,t,threshold,m,c),t,m)
                       for t in TILTS for m,c in ANGLES]
            bad,t,m = min(choices)
            if bad < 1:
                count = retained_count_lower(ball_count(D,energy),bad)
                grid.append({"E":energy,"T":threshold,"tilt":str(t),"directions":m,
                             "bad_upper_display":float(bad),"count_lower":count,
                             "count_lower_bits_display":log2(count),
                             "challenge_only_Q128_bits":bits_bound(F(128*198,count))})

    energy,threshold,t,a,f = 104,30,F(4,5),F(2,3),F(1,16)
    total = ball_count(D,energy)
    assert total == 20905094450944450994971371210796521612779265
    bad = ball_bad_bound(energy,t,threshold,12,F(933,1000))
    assert bad < F(1,3)
    count_lower = (2*total)//3+1
    moments = raw_ball_moments(energy)
    v0,g,variance_energy = moments["v0"],moments["g0"],moments["energy_variance"]
    assert g > 0 and variance_energy > 0
    assert g == variance_energy/(D*D)+(1-F(2,D))*moments["m22"]
    rho_squared = variance_energy*(1-a)/(D*D*a)
    assert 9-v0 > 0 and (9-v0)**2 > g/(a*f)
    assert v0 < F(25,16) and rho_squared < F(1,16)**2
    assert 15 < F(31,8)**2
    assert (F(25,16)+F(1,16))*(1+F(31,8)) == F(507,64) < 9
    common_denominator = v0.denominator
    assert moments["m4"].denominator == moments["m22"].denominator == common_denominator
    A,B,C = v0.numerator,moments["m4"].numerator,moments["m22"].numerator
    G = (125*C+B)*common_denominator-64*A*A
    V = (B+63*C)*common_denominator-64*A*A
    assert g == F(G,64*common_denominator**2)
    assert rho_squared == F(V,128*common_denominator**2)
    assert 8*(9*common_denominator-A)**2 > 3*G
    assert 16*A < 25*common_denominator and 2*V < common_denominator**2

    q,Q = 4294967197,128
    challenge_only = F(Q*198,count_lower)
    total_stat = Q*(F(198,count_lower)+F(7,2**164)+F(7,q**6)
                   +F(7,q**32)+F(1,2**160))
    assert challenge_only < F(1,2**128)
    assert total_stat < F(1,2**128)
    assert F(479,528)**7 > F(1,2)

    # Decoder correctness in complete small spaces and selected large ranks.
    decoder_cases = 0
    for d,budget in ((2,3),(3,5),(4,5)):
        expected = tuple(c for c in product((-2,-1,0,1,2),repeat=d) if sum(x*x for x in c)<=budget)
        assert len(expected) == ball_count(d,budget)
        for rank,c in enumerate(expected):
            assert ball_unrank(d,budget,rank) == c
            assert ball_rank(c,budget) == rank
            decoder_cases += 1
    for rank in (0,1,total//2,total-2,total-1):
        c = ball_unrank(D,energy,rank)
        assert sum(x*x for x in c) <= energy
        assert ball_rank(c,energy) == rank
        decoder_cases += 1

    print(json.dumps({
        "scope":"exact count/tail/moment arithmetic; no prover or security estimator",
        "shell71_count":count71,"shell71_count_bits_display":log2(count71),
        "shell71_tilt_probability_exact":str(shell_probability),
        "shell71_tilt_probability_display":float(shell_probability),
        "shell71_rows":shell_rows,
        "shell_entropy_obstruction": {str(e):{"count":shell_count(D,e),"bits_display":log2(shell_count(D,e))}
                                      for e in (71,84,88,112,116)},
        "ball104_T30":{
            "raw_count":total,"raw_count_bits_display":log2(total),
            "tilt":str(t),"tilted_symbol_weights":[256,500,625,500,256],
            "tilted_weight_sum":2137,"tilted_variance":"3048/2137",
            "directions":12,"cosine_squared_lower":"933/1000",
            "exp_lower_Taylor_degree":80,
            "bad_upper_exact":str(bad),"bad_upper_display":float(bad),
            "acceptance_lower_strict":"2/3","count_lower":count_lower,
            "count_lower_bits_display":log2(count_lower),
            "deterministic_energy_cap":energy,"operator_cap_strict":threshold,
            "raw_moments_exact":{name:str(value) for name,value in moments.items()},
            "raw_moments_display":{name:float(value) for name,value in moments.items()},
            "rho_squared_exact":str(rho_squared),
            "Gamma_squared_coefficient":9,
            "Gamma_first_squared_margin_exact":str((9-v0)**2-g/(a*f)),
            "Q128_full_statistical_error_exact":str(total_stat),
            "Q128_full_statistical_error_bits_display":-log2(total_stat),
            "Q128_full_statistical_error_guaranteed_bits":bits_bound(total_stat),
            "honest_failure_Q128_bound":"strictly less than 2^-128, under reviewed H640 ordinary schedule"
        },
        "bounded_grid":grid,"exact_decoder_cases":decoder_cases,
        "small_non_iid_moment_checks":small_general_moment_checks(),
        "limitations":"No new recursive digit/rank schedule or numerical MSIS hardness is certified."
    },indent=2))


if __name__ == "__main__":
    main()
