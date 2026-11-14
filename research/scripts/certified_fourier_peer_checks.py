"""Independent edge checks for the certified Fourier predicate.

These checks intentionally change precision, force the exact fallback, and use
closed spectral formulas. They are pure arithmetic, not a challenge sampler.
"""
import json
from fractions import Fraction as F
from itertools import product

import certified_fourier_predicate as predicate


def checks():
    coarse=[]
    for bits in (1,2,4,8):
        table=predicate.build_certified_table(4,bits=bits)
        paths={}
        for coefficients in product(range(-2,3),repeat=4):
            energy=sum(value*value for value in coefficients)
            c0,c1,c2,c3=coefficients
            cross=c0*c1+c1*c2+c2*c3-c0*c3
            for threshold in range(1,10):
                answer,path=predicate.certified_fourier_op_below(
                    coefficients,threshold,table,True)
                margin=threshold*threshold-energy
                expected=margin>0 and margin*margin>2*cross*cross
                assert answer==expected
                paths[path]=paths.get(path,0)+1
        coarse.append(dict(bits=bits,cases=5625,paths=paths))

    equality_cases=0
    for degree in (2,4,8,16,64):
        table=predicate.build_certified_table(degree)
        assert predicate.certified_fourier_op_below([0]*degree,1,table,True)==(
            True,'interval_accept')
        for position in range(degree):
            for value in (-2,-1,1,2):
                coefficients=[0]*degree
                coefficients[position]=value
                answer,path=predicate.certified_fourier_op_below(
                    coefficients,abs(value),table,True)
                assert answer is False
                equality_cases+=1

    rounding_cases=0
    for denominator in range(1,25):
        for numerator in range(-200,201):
            value=F(numerator,denominator)
            nearest=predicate._nearest_integer(value)
            assert abs(F(nearest)-value)<=F(1,2)
            if denominator==2 and numerator%2:
                assert nearest==(numerator+1)//2
            rounding_cases+=1

    interval_cases=0
    for terms in (1,2,3,7,24):
        for bits in (2,8,40,80):
            lower,upper=predicate.certified_pi_interval(terms,bits)
            fine_lower,fine_upper=predicate.certified_pi_interval(terms+10,bits+10)
            assert lower<=fine_lower<fine_upper<=upper
            interval_cases+=1
    return dict(coarse_precision=coarse,monomial_equality_cases=equality_cases,
                nearest_rounding_cases=rounding_cases,pi_nested_interval_cases=interval_cases)


if __name__=='__main__':
    print(json.dumps(checks(),indent=2))
